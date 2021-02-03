from common import database_API
import json ,os
from random import randint
import discord
from discord.ext import commands
from discord import Guild, Member, Message, Reaction, Role
from PIL import Image, ImageDraw, ImageFont ,ImageEnhance
import io

class profile_base():
    def __init__(self, icon_jpg:bytes, display_name:str, user_neme:str, rank_num:int, rank_:int, coin_num:int, xp_num:int, banner_jpg:bytes):
        self.display_name = display_name
        self.user_name = user_neme
        self.rank_num = rank_num
        self.rank_ = rank_
        self.image = Image.new('RGBA', (934,282), (0, 0, 0, 0))
        if banner_jpg != None:
            self.set_backgrount(banner_jpg)
        self.set_base_model()
        if icon_jpg != None:
            self.past_icon(icon_jpg)
        self.coin_num = coin_num
        self.xp_num = xp_num
        self.set_member_text()
        self.set_rank_text()
        self.set_xp_progress_and_coin_num()
    def set_backgrount(self, data):
        image_bk =  Image.open(io.BytesIO(data))
        re_bk = image_bk.resize((934, int(934*image_bk.size[1]/image_bk.size[0])), Image.ANTIALIAS)
        t_pos = (re_bk.size[1]-282)/2 if (re_bk.size[1]-282)/2 > 0 else (282-re_bk.size[1])/2
        re_bk = re_bk.crop((0, t_pos, re_bk.size[0], re_bk.size[1]))
        image_bk.close()
        self.image.paste(re_bk, (0,0))
        re_bk.close()
    def set_base_model(self):
        image_base = Image.open("card_base.png")
        if image_base.mode != 'RGBA':
            image_base_rgba=image_base.convert('RGBA')
            image_base.close()
        else:
            image_base_rgba= image_base
        alpha = image_base_rgba.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(0.6)
        image_base_rgba.putalpha(alpha)
        self.image=Image.composite(image_base_rgba, self.image, image_base_rgba)
    def past_icon(self, data):
        image_icon=Image.open(io.BytesIO(data))
        self.image.paste(image_icon.resize((142,142)), (60, 70))
        image_icon.close()
    def set_member_text(self):
        member_name_font = ImageFont.truetype(font=r'./ttf/NotoSansCJKtc-Regular.otf', size=46,encoding='utf-8')
        user_name_font = ImageFont.truetype(font=r'./ttf/NotoSansCJKtc-Regular.otf', size=27,encoding='utf-8')
        draw = ImageDraw.Draw(self.image)
        draw.text((250,110), self.display_name, font=member_name_font)
        draw.text((250+draw.textsize(self.display_name, font=member_name_font)[0]+20, 110+24), '('+self.user_name+')', font=user_name_font, fill='#ADADAD')
        
    def set_rank_text(self):
        draw = ImageDraw.Draw(self.image)
        level_1_text = '等級'
        level_1_size =  26
        level_1_font = ImageFont.truetype(font=r'./ttf/NotoSansCJKtc-Regular.otf', size=level_1_size,encoding='utf-8')

        level_2_text = str(self.rank_)
        level_2_size = 48
        level_2_font = ImageFont.truetype(font=r'./ttf/NotoSansCJKtc-Regular.otf', size=level_2_size,encoding='utf-8')

        rank_1_text = '排名'
        rank_1_size = 26
        rank_1_font = ImageFont.truetype(font=r'./ttf/NotoSansCJKtc-Regular.otf', size=rank_1_size,encoding='utf-8')

        rank_2_text = '#'+str(self.rank_num)
        rank_2_size = 48
        rank_2_font = ImageFont.truetype(font=r'./ttf/NotoSansCJKtc-Regular.otf', size=rank_2_size,encoding='utf-8')

        x_base = 934 - 60
        x_base -= draw.textsize(level_2_text, font=level_2_font)[0]
        draw.text((x_base, 48), level_2_text, font=level_2_font ,fill='#FF0000')
        x_base -= (draw.textsize(level_1_text, font=level_1_font)[0] + 5)
        draw.text((x_base, 70), level_1_text, font=level_1_font ,fill='#FF0000')
        x_base -= (draw.textsize(rank_2_text, font=rank_2_font)[0]+15)
        draw.text((x_base, 48), rank_2_text, font=rank_2_font )
        x_base -= (draw.textsize(rank_1_text, font=rank_1_font)[0]+10)
        draw.text((x_base, 70), rank_1_text, font=rank_1_font )

    def set_xp_progress_and_coin_num(self):
        draw = ImageDraw.Draw(self.image)
        common_size = 27
        common_font = ImageFont.truetype(font=r'./ttf/NotoSansCJKtc-Regular.otf', size=common_size, encoding='utf-8')
        
        text_list_1 = ('硬幣:', str(self.coin_num))
        text_list_fill_1 = ('#E1E100', '#F9F900')[::-1]
        text_list_2 = (str(self.xp_num), '/', str(database_API.calcuelate_xp(self.rank_ + 1)), 'XP')
        text_list_fill_2 = ('#FFFFFF', '#ADADAD', '#ADADAD', '#ADADAD')[::-1]

        x_base = 934 - 60 - 30
        y = 171+15
        for i,t in enumerate(text_list_2[::-1]):
            offset = draw.textsize(t, font=common_font)
            x_base -= (offset[0]+5)
            draw.text((x_base, y), t, fill=text_list_fill_2[i], font=common_font)
        x_base -= 15
        for i,t in enumerate(text_list_1[::-1]):
            offset = draw.textsize(t, font=common_font)
            x_base -= (offset[0]+5)
            draw.text((x_base, y), t, fill=text_list_fill_1[i], font=common_font)

def load_json_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as fp:
            j = json.load(fp)
            fp.close()
            return j
    else:
        return False

class profile(commands.Cog):
    def __init__(self, client):
        self.bot = client
    

    @commands.Cog.listener('on_guild_role_delete')
    async def profile_on_guild_role_delete(self, role:Role):
        role_dict = load_json_file(str(role.guild.id)+'rank_role.json')
        if role_dict != False:
            for tem in role_dict:
                if not tem.startswith('per'):
                    if role_dict[tem]['id'] == role.id:
                        new_role = await role.guild.create_role(role)
                        role_dict[tem]['id'] = new_role.id
                        role_dict[tem]['name'] = new_role.name
            with open(str(role.guild.id)+'rank_role.json', mode="w", encoding='utf-8') as fp:
                json.dump(role_dict, fp)
                fp.close()

    @commands.Cog.listener('on_guild_role_update')
    async def profile_on_guild_role_update(self, before:Role, after:Role):
        if before.id != after.id:
            role_dict = load_json_file(str(before.guild.id)+'rank_role.json')
            if role_dict != False:
                for tem in role_dict:
                    if not tem.startswith('per') and role_dict[tem]['id'] == before.id:
                        role_dict[tem]['id'] = after.id
                with open(str(before.guild.id)+'rank_role.json', "w", encoding='utf-8') as fp:
                    json.dump(role_dict, fp)
                    fp.close
                    


    @commands.Cog.listener('on_message')
    async def profile_on_message(self, message:Message):
        ctx = await self.bot.get_context(message)
        member = message.guild.get_member(message.author.id)
        if ctx.command == None and ctx.author.id != self.bot.user.id:
            increase_num = randint(10,25)
            rank = database_API.increase_xp(message.guild.id, message.author.id, increase_num)
            if rank != False:
                rank = rank[0]
                rankup_channel_id = database_API.get_message_channel_id(message.guild.id, 'rank_up_channel_id')
                if rankup_channel_id != None:
                    await message.guild.get_channel(rankup_channel_id).send('<@!{}> 等級 提升到 {} 啦!'.format(message.author.id, database_API.get_member_row(message.guild.id, message.author.id)[database_API.member_index.rank]))
                else:
                    await message.channel.send('<@!{}> 等級 提升到 {} 啦!'.format(message.author.id, database_API.get_member_row(message.guild.id, message.author.id)[database_API.member_index.rank]))

                role_dict=load_json_file(str(message.guild.id)+'rank_role.json')
                if rank%20 == 0:
                    if role_dict != False:
                        for i in range(100, 19, -20):
                            if i == rank:
                                t_role = message.guild.get_role(role_dict["rank_{}".format(i)]["id"])
                                await member.add_roles(t_role)
                                t_role = message.guild.get_role(role_dict["rank_{}".format(i-20)]["id"])
                                await member.remove_roles(t_role)
                                t_rmbed = discord.Embed()
                                t_rmbed.description = '恭喜{} <@!{}> 成長為 {}'.format(ctx.guild.get_role(role_dict["rank_{}".format(i-20)]["id"]).name, message.author.id, ctx.guild.get_role(role_dict["rank_{}".format(i)]["id"]).name)
                                await message.channel.send(embed= t_rmbed)
                                if rankup_channel_id != None:
                                    await message.guild.get_channel(rankup_channel_id).send(embed= t_rmbed)
                                break
                if rank == 1:
                    t_role = message.guild.get_role(role_dict["rank_0"]["id"])
                    await message.author.add_roles(t_role)
                    t_rmbed = discord.Embed()
                    t_rmbed.description = '恭喜<@!{}> 成為 {}'.format(message.author.id, ctx.guild.get_role(role_dict["rank_0"]["id"]).name)
                    await message.channel.send(embed= t_rmbed)
                    if rankup_channel_id != None:
                        await message.guild.get_channel(rankup_channel_id).send(embed= t_rmbed)
            database_API.increase_normal_coin(message.guild.id, message.author.id, increase_num)

    @commands.Cog.listener('on_guild_join')
    async def profile_guild_join(self, guild:Guild):
        database_API.creat_server_member_table(guild.id)
        members = guild.members
        members_set = set()
        for member in members:
            if member.id == self.bot.user.id or member.bot:
                continue
            members_set.add((member.id, 0, 0, json.dumps([]), 0, json.dumps([]), None, None))
        database_API.add_members(guild.id, members_set)
    
    @commands.Cog.listener('on_member_join')
    async def profile_member_join(self, member:Member):
        if database_API.get_member_row(member.guild.id, member.id) != None :
            return
        if not member.bot:
            database_API.add_member(member.guild.id, member.id)

    @commands.Cog.listener('on_reaction_add')
    async def profile_on_reaction_add(self, reaction:Reaction, member:Member):
        message=reaction.message
        increase_num = randint(0,5)
        if not member.bot and not reaction.message.author.bot:
            database_API.increase_normal_coin(message.guild.id, message.author.id, increase_num)
        

    @commands.group(name = 'profile', invoke_without_command = True)
    async def profile_profile_group(self, ctx, *attr):
        tem_dict = load_json_file(str(ctx.guild.id)+'rank_role.json')
        if tem_dict!=False:
            if tem_dict['per_channel'] != ctx.channel.id and tem_dict['per_channel'] != 0:
                await ctx.channel.send("請至<#{}>輸入指令".format(tem_dict['per_channel']))
                return
        avatar_url = ctx.author.avatar_url_as(format='jpg', size=1024)
        if avatar_url._url != None:
            icon_jpg_data = await avatar_url.read()
        else:
            icon_jpg_data = None
        banner_url = ctx.guild.banner_url
        banner_jpg_data = None
        if ctx.author.id == 326752816238428164 or ctx.author.id == 222677011917832202 or ctx.author.id == 428456132625956865:
            with open('shina_only.jpg', "rb") as fp:
                banner_jpg_data = fp.read()
                fp.close()
        elif banner_url._url != None:
            banner_jpg_data = await banner_url.read()
        else:
            with open("banner_None.png", "rb") as fp:
                banner_jpg_data = fp.read()
                fp.close()
        member_row =  database_API.get_member_row(ctx.guild.id, ctx.author.id)
        rank_num = database_API.sort_rank_num(ctx.guild.id,member_row[database_API.member_index.xp])
        profile = profile_base(icon_jpg_data, ctx.author.display_name, str(ctx.author), rank_num, member_row[database_API.member_index.rank], member_row[database_API.member_index.normal_coin], member_row[database_API.member_index.xp], banner_jpg_data)

        fp = open(str(ctx.author.name)+'.png','wb')
        profile.image.save(fp,format='PNG')
        fp.close()
        profile.image.close()
        fp = open(str(ctx.author.name)+'.png','rb')
        dfp = discord.File(fp,"profile.png")
        await ctx.channel.send(file=dfp)
        dfp.close()
        fp.close()
        os.remove(str(ctx.author.name)+'.png')


    @profile_profile_group.command(name = 'set_rankup_channel')
    async def profile_group_set_upgrade_channel(self, ctx, *argv):
        if len(argv) == 1:
            ch_id = argv[0]
            ch_id = ch_id[2:-1]
            if str(ch_id).isdigit():
                channel = ctx.guild.get_channel(int(ch_id))
                if channel != None:
                    database_API.set_rankup_channel(ctx.guild.id, channel.id)
                    await ctx.channel.send("設定升級訊息至頻道:{}".format(channel.name))
                    return
        await ctx.channel.send("錯誤的頻道 :{}".format(ctx.message.content))
        
    @profile_profile_group.command(name = "init_role")
    async def profile_group_init_role_command(self, ctx:discord.ext.commands, *argv):
        f_msg = await ctx.channel.send("初始化等級位階身分組....")
        default_dict = {}
        if not os.path.exists(str(ctx.guild.id)+'rank_role.json'):
            with open("default_rank_roles.json", "r", encoding='utf-8') as fp:
                default_dict = json.load(fp)
        else:
            await ctx.channel.send("發現原有資料，使用舊資料同步...")
            with open(str(ctx.guild.id)+'rank_role.json', "r", encoding='utf-8') as fp:
                default_dict = json.load(fp)
        target_guild = ctx.guild
        for tem in default_dict:
            if tem.startswith('per'):
                continue
            has_role = False
            for role in ctx.guild.roles:
                if role.name == default_dict[tem]["name"] or role.id == default_dict[tem]["id"]:
                    has_role = role
                    break
            if has_role != False:
                default_dict[tem]["id"] = has_role.id
                default_dict[tem]["name"] = role.name
                await ctx.channel.send("發現{}已經存在，進行綁定".format(has_role.name))
            else:
                await f_msg.edit(content= str(f_msg.content)+'\n創建身分組{} ....'.format(default_dict[tem]['name']))
                new_role = await target_guild.create_role(name= default_dict[tem]['name'], permissions= discord.Permissions(0),colour= discord.Colour(default_dict[tem]['color']), mentionable= False, hoist=False)
                default_dict[tem]["id"] = new_role.id
        await ctx.channel.send("等級位階身分組初始化完成。")
        await ctx.channel.send("分配身分組....")
        member_table = database_API.get_members_table(target_guild.id)
        for row in member_table:
            t_rank = row[database_API.member_index.rank]
            member_id = row[database_API.member_index.member_id]
            member = target_guild.get_member(member_id)
            def role_exist(role_id:int, member:Member):
                f = False
                for role in member.roles:
                    if role.id == role_id:
                        f =True
                        break
                return f
            if member == None:
                print('WORNING!!!! id:{} cant get member'.format(member_id))
            if t_rank > 0:
                if not role_exist(default_dict["rank_0"]["id"], member):
                    await member.add_roles(target_guild.get_role(default_dict["rank_0"]["id"]))
            remove_list = []
            for i in range(0, 101, 20):
                remove_list.append(default_dict["rank_{}".format(i)]["id"])
                if t_rank >= i and t_rank < i+20:
                    if not role_exist(default_dict["rank_{}".format(i)]["id"], member):
                        await member.add_roles(target_guild.get_role(default_dict["rank_{}".format(i)]["id"]))
                    for m_role in member.roles:
                        if m_role.id in  remove_list[:-1]:
                            await member.remove_roles(m_role)
                            
                    remove_list = []

            
        await ctx.channel.send("分配身分組完成。")
        await ctx.channel.send("設定權限身分組....")
        if target_guild.get_role(770218792440823820):
            await ctx.channel.send("偵測到預設身分組{}".format(target_guild.get_role(770218792440823820).name))
            default_dict['permissions'].append(770218792440823820)
        await ctx.channel.send("設定權限身分組完成。")
        with open(str(target_guild.id)+'rank_role.json', 'w', encoding='utf-8') as fp:
            json.dump(default_dict, fp)
            fp.close()
        await ctx.channel.send("初始化身分組完成。")

    @profile_profile_group.command(name= 'bind_commad_channel')
    async def profile_group_bind_commad_channel(self, ctx:discord.ext.commands, *argv):
        tem_dict = load_json_file(str(ctx.guild.id)+'rank_role.json')
        if tem_dict == False:
            await ctx.channel.send("請先初始化，輸入`!profile init_role`")
            return
        if len(tem_dict['permissions']) > 0:
            member = ctx.guild.get_member(ctx.message.author.id)
            f = True
            for m_role in member.roles:
                if m_role.id  in tem_dict['permissions']:
                    f= False
                    if len(argv)>0:
                        channel_id = argv[0][2:-1]
                        if str(channel_id).isdigit():
                            channel_id= int(channel_id)
                            if ctx.guild.get_channel(channel_id) != None:
                                tem_dict['per_channel'] = channel_id
                                with open(str(ctx.guild.id)+'rank_role.json', "w", encoding='utf-8') as fp:
                                    json.dump(tem_dict, fp)
                                    fp.close()
                                await ctx.channel.send("設定<#{}>為profile 指令輸入頻道".format(channel_id))
                            else:
                                await ctx.channel.send("找不到<#{}>")
                        else:
                            await ctx.channel.send("傳入值錯誤:{}".format(argv[0]))
                    else:
                        await ctx.channel.send("請輸入傳入值:頻道名稱(可以連結的)")
                    return
            if f:
                await ctx.channel.send("你沒有使用這個指令的權限")
                return
        else:
            if len(argv)>0:
                channel_id = argv[0][2:-1]
                if str(channel_id).isdigit():
                    channel_id= int(channel_id)
                    if ctx.guild.get_channel(channel_id) != None:
                        tem_dict['per_channel'] = channel_id
                        with open(str(ctx.guild.id)+'rank_role.json', "w", encoding='utf-8') as fp:
                            json.dump(tem_dict, fp)
                            fp.close()
                        await ctx.channel.send("設定<#{}>為profile 指令輸入頻道".format(channel_id))
                    else:
                        await ctx.channel.send("找不到<#{}>")
                else:
                    await ctx.channel.send("傳入值錯誤:{}".format(argv[0]))
            else:
                await ctx.channel.send("請輸入傳入值:頻道名稱(可以連結的)")

def setup(client):
    client.add_cog(profile(client))
