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
    - Owner: Takanashi Kiara, a youtuber working under company Hololive.
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
            if image_bytes:
                # 1. Create the Image Part object
                input_image = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/png" # Discord avatars are usually png/webp
                )
                
                # 2. Call Gemini 3 Pro Image (Multimodal)
                response = await self.client.aio.models.generate_content(
                    model='gemini-2.5-flash-image', 
                    contents=[prompt, input_image],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"], # Force image output
                        safety_settings=[types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_LOW_AND_ABOVE"
                        )]
                    )
                )
                
                # 3. Extract Inline Image Data
                # generate_content returns 'candidates', not 'generated_images'
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        return part.inline_data.data # This is the raw bytes
                return "Error: Model returned text instead of an image."
            else:
                response = await self.client.aio.models.generate_content(
                    model='gemini-2.5-flash-image', 
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"], # Force image output
                        safety_settings=[types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold="BLOCK_LOW_AND_ABOVE"
                        )]
                    )
                )
                return response.generated_images[0].image.image_bytes
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
        history = self.get_recent_history(user_id)
        history.append({"role": "user", "parts": [{"text": f"User ({ctx.author.display_name}): {user_text}"}]})

        # 3. Define Tools
        draw_tool = types.Tool(
            function_declarations=[
                types.FunctionDeclaration(
                    name="generate_image",
                    description="Generates an image. If the user wants to be in the picture, set use_profile_image to true.",
                    parameters=types.Schema(
                        type="OBJECT",
                        properties={
                            "prompt": types.Schema(type="STRING", description="Visual description."),
                            "use_profile_image": types.Schema(type="BOOLEAN", description="Set true if drawing the user/avatar.")
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
                                
                                # Logic: Did the model ask for the profile image?
                                avatar_bytes = None
                                if fn.args.get('use_profile_image', False):
                                    avatar_bytes = await self.get_user_avatar_bytes(ctx.author)
                                
                                # Call the tool
                                image_data = await self._tool_generate_image(fn.args['prompt'], avatar_bytes)
                                
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