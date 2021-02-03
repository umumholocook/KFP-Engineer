
async def clear_lines(ctx, number:int):
    msg_list = await ctx.channel.history(limit = number).flatten()
    for msg in msg_list:
        if msg != ctx.message:
            await msg.delete()
async def clear_user_msg(ctx, user_id, number = 20):
    msg_list = await ctx.channel.history(limit=200).flatten()
    for msg in msg_list:
        if msg.author.id ==  user_id and number > 0 and msg != ctx.message:
            print("delet {}".format(msg.content))
            await msg.delete()
            number -= 1
async def clear_overmsg(ctx, number):
    msg_list = await ctx.channel.history(limit = 200).flatten()
    for msg in msg_list:
        if msg.content.startswith('//') and number > 0:
            await msg.delete()
            number -= 1