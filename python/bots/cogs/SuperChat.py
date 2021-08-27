from discord import AllowedMentions, File, User
from discord.ext import commands

from datetime import timezone
import logging

from jinja2 import Template

from common import (
    AssetCache, DatetimeUtil,
    UnicodeEmoji as uemoji,
    SimpleDiscordMarkdown as sdcmd
)
from common.MemberUtil import MemberUtil
from common.SimpleDiscordMarkdown.Datatypes import (
    MentionData, MentionType, TimestampData, EmojiData
)
from common.SuperChatUtil import ColorRank, render

class SuperChatMeme(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='sc', invoke_without_command=True)
    async def superchat_group(self, ctx: commands.Context,
                              sc_money: int, recipient: User, *, sc_msg: str=''):
        rank = ColorRank.judge(sc_money)
        
        # check sc_money too little or not
        if not rank:
            await ctx.send(f'至少 `{rank.upperbound()}` 硬幣才能使用 SuperChat!')
            return
        
        # check sc_msg too long or not
        if len(sc_msg) > rank.lengthlimit:
            await ctx.send(f'字數過多! 請限制在 `{rank.lengthlimit}` 字數內!')
            return
            
        # check author have enough coins or not
        giver = MemberUtil.get_or_add_member(ctx.author.id)
        if giver.coin < sc_money:
            await ctx.send('硬幣不足! 快去店外雜談區聊天賺硬幣!')
            return
        taker = MemberUtil.get_or_add_member(recipient.id)
        
        adverb = '很寒酸的施捨' if sc_money == ColorRank(0).upperbound() else ''
        unsalted = ' ' if sc_msg or adverb else 'Unsalted '
        appreciation = (f'感謝 {ctx.author.mention} {adverb}給'
                        f' {recipient.mention} 的{unsalted}SuperChat!')
        
        # 解析訊息為語法結構，data 蒐集了 syntaxnode 裡所參照的資料
        syntaxnode, data = sdcmd.parse(sc_msg)
        
        async with ctx.channel.typing():
            # 以下可能很耗時
            try:
            
                author_name = ctx.author.display_name
                author_avatar = ctx.author.avatar_url_as(format='png', size=128)
                author_avatar = await AssetCache.read_as_dataurl(author_avatar)
                
                await self.extensionalize(data, ctx)
            
                async with render(
                    author_name, author_avatar, sc_money, rank,
                    sc_msg, syntaxnode, data, zoom=2
                ) as imgfp:
                    file = File(imgfp, filename='superchat.png')
                    await ctx.send(appreciation, file=file,
                                   allowed_mentions=AllowedMentions.none())
            except Exception as ex:
                ctx.send('未送出訊息，不明的錯誤')
                raise ex
            else:
                MemberUtil.add_coin(member_id=giver.member_id, amount=-sc_money)
                MemberUtil.add_coin(member_id=taker.member_id, amount=sc_money*.8)
                MemberUtil.add_coin(member_id=self.bot.user.id, amount=sc_money*.2)
                
    
    help_msg = Template(
'''```歡迎大家使用 SuperChat 功能! 使用方法如下:
!sc <硬幣數量> <使用者> <文字> 給該使用者多少硬幣，後面文字可留言
每個等級對應的 SuperChat 字數上限如下:
{% for rank in ranks if rank -%}
> Coin. {{ rank.lowerbound() }}
{%- if rank.upperbound() %}-{{ rank.upperbound()-1 }} {% else %}以上 {% endif -%}
{{ rank.lengthlimit }}字元{% if not rank.lengthlimit %}(無法留言){% endif %}
{% endfor -%}
註1: 避免洗版，有圖像有行數與高度限制
註2: 支援 Discord Markdown，大致所見接近所得
註3: 行末要加兩個空白才會真正在圖像的訊息上換行
註4: 每次 SuperChat 酌收 20% 手續費，故該使用者只會收到 80% 的硬幣```''',
    ).render(ranks=ColorRank)
            
    @superchat_group.command()
    async def help(self, ctx: commands.Context):
        await ctx.send(self.help_msg)
    
    @staticmethod
    async def extensionalize(data, ctx):
        '''得到脈絡中的資料，參照回原始資料'''
        for d in data:
            if isinstance(d, EmojiData):
                try:
                    if d.is_unicode_emoji:
                        emoji = uemoji.Emoji(d.id)
                        d.src = emoji.url_as(format='png')
                    else:
                        emoji = ctx.bot.get_emoji(d.id)
                        asset = emoji.url_as(format='png') if emoji else (d, 'png')
                        d.src = await AssetCache.read_as_dataurl(asset)
                except Exception as ex:
                    logging.warning(ex)
            elif isinstance(d, MentionData):
                try:
                    if d.type == MentionType.USER:
                        user = ctx.bot.get_user(d.id)
                        d.display_name = user.display_name
                    elif d.type == MentionType.CHANNEL:
                        channel = ctx.bot.get_channel(d.id)
                        d.display_name = channel.name
                    elif d.type == MentionType.ROLE:
                        role = ctx.guild.get_role(d.id)
                        d.display_name = role.name
                    elif d.type == MentionType.EVERYONE:
                        d.display_name = 'everyone'
                    elif d.type == MentionType.HERE:
                        d.display_name = 'here'
                except AttributeError:
                    d.display_name = str(d.id)
            elif isinstance(d, TimestampData):
                # 一個坑
                # https://github.com/Rapptz/discord.py/blob/1863a1c6636f53592519320a173ec9573c090c0b/discord/utils.py#L121
                # 上面原始碼 discord.py 對於 datatime 或許沒寫好，應該要寫成
                # def snowflake_time(id):
                #     return datetime.datetime.fromtimestamp(((int(id) >> 22) + DISCORD_EPOCH) / 1000, timezone.utc)
                # 否則將會誤將 utc+0 的 timestamp，相同值直接被視為 utc+8 的 timestamp
                # 參考 https://docs.python.org/3/library/datetime.html#datetime.datetime.utcfromtimestamp
                # 原來有人發過 issue 了ノಠ_ಠノ https://github.com/Rapptz/discord.py/issues/5921
                created_at = ctx.message.created_at.replace(tzinfo=timezone.utc).timestamp()
                d.str = DatetimeUtil.strptime(d.timestamp, d.style, origintimestamp=created_at)

def setup(client):
    client.add_cog(SuperChatMeme(client))