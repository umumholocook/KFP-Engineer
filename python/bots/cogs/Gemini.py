import discord
import io
import sqlite3
import time
import requests
from PIL import Image
from discord import User
from discord.ext import commands
from google import genai
from google.genai import types

class Gemini(commands.Cog):
    # Gemini 3.0 System Instructions
    # Note: Gemini 3 prefers concise, direct instructions over complex "personas" unless specified.
    SYSTEM_INSTRUCTIONS = """You are 幕後大總管 (Grand Manager), a bot at KFP (Kiara Fried Phoenix).
    - Owner: Takanashi Kiara, a virtual youtuber working under company, in the group Hololive EN. Often referred as 店長.
    - Greet with: Kikkeriki.
    - Language: Traditional Chinese (繁體中文).
    - Personality: Helpful, human-like, use display names.
    - CAPABILITY: You can generate images. If a user asks for a picture, drawing, or visual, USE the 'generate_image' tool. Do not just describe it in text.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.client = genai.Client()
        
        # Initialize Database
        self.db_name = "bot_memory.db"
        self.init_db()

    # --- Database & Helper Functions (Same as before) ---
    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS history
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, role TEXT, content TEXT)''')
        conn.commit()
        conn.close()

    def add_to_history(self, user_id, role, content):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
        c.execute("DELETE FROM history WHERE id NOT IN (SELECT id FROM history WHERE user_id = ? ORDER BY id DESC LIMIT 50) AND user_id = ?", (user_id, user_id))
        conn.commit()
        conn.close()

    def get_recent_history(self, user_id, limit=20):
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute("SELECT role, content FROM history WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit))
        rows = c.fetchall()
        conn.close()
        return [{"role": r, "parts": [{"text": c}]} for r, c in reversed(rows)]
    
    async def get_user_avatar_bytes(self, user: discord.User) -> bytes:
        """Downloads the user's avatar in an async way to prevent bot freezing."""
        if not user.display_avatar:
            return None
        # Read directly into bytes (no requests library needed)
        return await user.display_avatar.read()

    async def _tool_generate_image(self, prompt: str, image_bytes: bytes = None):
        print(f"🎨 Tool Triggered: {prompt}")
        try:
            # Prepare contents
            contents = [prompt]
            if image_bytes:
                # Create the Image Part object
                input_image = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/png" # Discord avatars are usually png/webp
                )
                contents.append(input_image)
            
            # Call Gemini 3 Pro Image (Multimodal)
            response = await self.client.aio.models.generate_content(
                model='gemini-2.5-flash-image', 
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"], # Force image output
                    safety_settings=[types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_ONLY_HIGH"
                    )]
                )
            )
            
            # 3. Extract Inline Image Data safely
            if not response.candidates:
                return "Error: No candidates returned. The prompt might have triggered a safety filter."
            
            first_candidate = response.candidates[0]
            if not first_candidate.content or not first_candidate.content.parts:
                # Check for finish_reason if available for debugging info
                reason = "Unknown"
                if hasattr(first_candidate, 'finish_reason'):
                     reason = str(first_candidate.finish_reason)
                return f"Error: No content generated. Finish Reason: {reason}"

            for part in first_candidate.content.parts:
                if part.inline_data:
                    return part.inline_data.data # This is the raw bytes
            
            return "Error: Model returned content but no image data found."

        except Exception as e:
            return f"API Error: {str(e)}"

    # ---------------- MAIN CHAT COMMAND ----------------
    @commands.group(name='chat', invoke_without_command=True)
    @commands.cooldown(1, 2, type=commands.BucketType.user) 
    async def chat(self, ctx: commands.Context):
        user_text = ctx.message.content.replace('!chat ', '').replace('!chat', '')
        if not user_text:
            await ctx.reply("Kikkeriki! 請問今天有什麼吩咐？")
            return

        user_id = ctx.author.id
        
        # 1. Send Initial Status
        status_msg = await ctx.reply("🤔 大總管思考中...")
        
        # 2. Prepare History
        # --- Handle Attachments ---
        user_parts = [{"text": f"User ({ctx.author.display_name}): {user_text}"}]
        attached_file_bytes = None # To store for potential drawing reference
        
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                # Limit size to 10MB to avoid API errors (Gemini has limits, Discord has limits) - roughly
                if attachment.size > 10 * 1024 * 1024:
                    continue
                    
                try:
                    # Download content
                    file_data = await attachment.read()
                    
                    # Store the FIRST image found as potential reference for drawing
                    if not attached_file_bytes and attachment.content_type and attachment.content_type.startswith('image/'):
                        attached_file_bytes = file_data
                    
                    # Determine how to handle the file based on MIME type and extension
                    mime_type = attachment.content_type.split(';')[0].strip() if attachment.content_type else ""
                    filename_lower = attachment.filename.lower()
                    
                    # 1. Supported Media Types (Images, Audio, Video, PDF)
                    # Note: Gemini supports application/pdf directly.
                    if mime_type.startswith(('image/', 'audio/', 'video/')) or mime_type == 'application/pdf':
                        part = types.Part.from_bytes(data=file_data, mime_type=mime_type)
                        user_parts.append(part)
                        print(f"📎 Attached media/pdf: {attachment.filename} ({mime_type})")
                    
                    # 2. Text/Code Files (Fallback to text content)
                    # If it's explicitly text/* OR acts like a code file
                    else:
                        is_likely_text = mime_type.startswith('text/') or filename_lower.endswith(
                            ('.py', '.js', '.html', '.css', '.json', '.md', '.txt', '.sh', '.c', '.cpp', '.h', '.java', '.go', '.rb', '.ts', '.yml', '.yaml', '.xml', '.ini', '.env')
                        )
                        
                        if is_likely_text:
                            try:
                                text_content = file_data.decode('utf-8')
                                # Format it clearly for the model
                                prompt_text = f"\n[Attached File: {attachment.filename}]\n```\n{text_content}\n```\n"
                                user_parts.append(types.Part.from_text(text=prompt_text))
                                print(f"📎 Attached text file: {attachment.filename} (converted to text)")
                            except UnicodeDecodeError:
                                print(f"⚠️ Could not decode {attachment.filename} as UTF-8 text.")
                        else:
                            print(f"⚠️ Skipping unsupported file type: {attachment.filename} ({mime_type})")

                except Exception as e:
                    print(f"Failed to read attachment {attachment.filename}: {e}")

        history = self.get_recent_history(user_id)
        history.append({"role": "user", "parts": user_parts})

        # 3. Define Tools
        draw_tool = types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="generate_image",
                    description="Generates an image. If the user wants to be in the picture, set use_profile_image to true. If the user provided an image attachment to use as reference, set use_attached_image to true.",
                    parameters=types.Schema(
                        type="OBJECT",
                        properties={
                            "prompt": types.Schema(type="STRING", description="Visual description."),
                            "use_profile_image": types.Schema(type="BOOLEAN", description="Set true if drawing the user/avatar."),
                            "use_attached_image": types.Schema(type="BOOLEAN", description="Set true if drawing based on the attached image.")
                        },
                        required=["prompt"]
                    )
                )
            ]
        )

        try:
            # 4. START STREAM (Gemini 3.0 Pro)
            # Note: stream=True is implied by iterating the response, but explicit call is safer in some SDKs
            # In google-genai SDK 1.0+, generate_content_stream is the method
            response_stream = await self.client.aio.models.generate_content_stream(
                model='gemini-3-pro-preview',
                contents=history,
                config=types.GenerateContentConfig(
                    system_instruction=self.SYSTEM_INSTRUCTIONS,
                    tools=[draw_tool],
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=True,
                    )
                )
            )

            # 5. The Throttled Loop
            final_text_buffer = ""
            current_thought_buffer = ""
            last_update_time = time.time()
            
            async for chunk in response_stream:
                if chunk.candidates and chunk.candidates[0].content.parts:
                    for part in chunk.candidates[0].content.parts:
                        
                        # A. Handle Thoughts (The "Thinking..." phase)
                        if hasattr(part, 'thought') and part.thought:
                            current_thought_buffer += part.text
                            
                            # THROTTLE CHECK: Only edit if > 1.5s passed
                            if time.time() - last_update_time > 1.5:
                                # Grab last 100 chars of thought to show "activity"
                                snippet = current_thought_buffer[-100:].replace('\n', ' ')
                                await status_msg.edit(content=f"🤔 大總管思考中...\n> ...{snippet}")
                                last_update_time = time.time()

                        # Text Answer
                        elif part.text:
                            final_text_buffer += part.text
                            if time.time() - last_update_time > 1.5:
                                display_text = final_text_buffer[:1900] + "..." if len(final_text_buffer) > 1900 else final_text_buffer
                                await status_msg.edit(content=display_text)
                                last_update_time = time.time()

                        # Function Call (Image)
                        elif part.function_call:
                            fn = part.function_call
                            if fn.name == "generate_image":
                                await status_msg.edit(content=f"🎨 大總管正在繪製: {fn.args['prompt']}...")
                                
                                # Logic: Determine which image to use as reference
                                reference_image_bytes = None
                                
                                # A. Check attached image request first
                                if fn.args.get('use_attached_image', False) and attached_file_bytes:
                                     reference_image_bytes = attached_file_bytes
                                # B. Check profile image request second (only if no attachment used, or override logic)
                                elif fn.args.get('use_profile_image', False):
                                    reference_image_bytes = await self.get_user_avatar_bytes(ctx.author)
                                
                                # Call the tool
                                image_data = await self._tool_generate_image(fn.args['prompt'], reference_image_bytes)
                                
                                if isinstance(image_data, bytes):
                                    file = discord.File(io.BytesIO(image_data), "kfp_art.png")
                                    await status_msg.delete() 
                                    await ctx.reply(file=file, content="完成！")
                                    
                                    self.add_to_history(user_id, "user", user_text)
                                    self.add_to_history(user_id, "model", f"[Generated image: {fn.args['prompt']}]")
                                    return 
                                else:
                                    await status_msg.edit(content=f"繪圖失敗: {image_data}")
                                    return

            # 6. Final Flush
            # The loop finishes, but we might have leftover text in the buffer that wasn't sent yet
            if final_text_buffer:
                if len(final_text_buffer) > 2000:
                    # Handle split logic if needed, for now just truncate
                    final_text_buffer = final_text_buffer[:1990] + "..."
                
                await status_msg.edit(content=final_text_buffer)
                
                # Save to DB
                self.add_to_history(user_id, "user", user_text)
                self.add_to_history(user_id, "model", final_text_buffer)

        except Exception as e:
            print(f"🔥 Error: {e}")
            error_msg = str(e)
            if "RESOURCE_EXHAUSTED" in error_msg:
                await status_msg.edit(content="⚠️ 額度已滿 (Quota Exceeded): Gemini 3.0 需要付費帳號才能使用。請檢查您的 Google Cloud Billing 設定。")
            else:
                await status_msg.edit(content=f"❌ 系統錯誤: {error_msg}")

async def setup(client):
    await client.add_cog(Gemini(client))