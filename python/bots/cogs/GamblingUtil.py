# 一些輔助性質的功能
import asyncio

class GamblingUtil():
    async def _create_loop(bot, embed, main_message, ctx, value_type, main_name, embed_index):
        def check(m):
            return m.channel == ctx.channel and m.author == ctx.author
        def reaction_check(reaction, user):
            if user == ctx.author and reaction.message == main_message:
                return str(reaction.emoji) == '⭕' or '❌'
            else:
                return False
        flag = True
        while flag:
            wait_msg = await bot.wait_for('message', check=check)
            if value_type == type(int()) and not wait_msg.content.isdigit():
                embed.set_field_at(embed_index,name= '設定{}-輸入的不是數字重新輸入'.format(main_name), value='請直接回覆{}'.format(main_name),inline=False)
                await wait_msg.delete()
                await main_message.edit(embed= embed)
                continue
            elif value_type != type(int()):
                pass
            embed.set_field_at(embed_index, name= '設定{}-確認⭕️取消❌'.format(main_name), value=wait_msg.content, inline=False)
            await wait_msg.delete()
            await main_message.edit(embed= embed)
            await main_message.add_reaction('⭕')
            await main_message.add_reaction('❌')
            try:
                get_reaction = await bot.wait_for('reaction_add', timeout=30.0, check=reaction_check)
            except asyncio.TimeoutError:
                embed.set_field_at(embed_index , name= '設定{}-等待反應超時'.format(main_name), value='error')
                await main_message.clear_reactions()
                await main_message.edit(embed= embed)
                return False
            else:
                if get_reaction[0].emoji == '⭕':
                    embed.set_field_at(embed_index , name= '設定{}-完成'.format(main_name), value=wait_msg.content)
                    flag = False
                elif get_reaction[0].emoji == '❌':
                    embed.set_field_at(embed_index ,name= '設定{}-重新輸入'.format(main_name), value='請直接回覆{}'.format(main_name),inline=False)
                await main_message.clear_reactions()
                await main_message.edit(embed= embed)
        return True