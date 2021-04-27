from discord.raw_models import RawReactionActionEvent, RawReactionClearEvent
from discord.utils import get
from common.models.ReactionRole import ReactionMessage
from common.Util import Util
from discord.ext import commands

class ReactionRoleUtil():
    def addReaction(bot: commands.Bot, payload: RawReactionActionEvent):
        type: Util.ReactionType = ReactionRoleUtil.__findMessageRecord(payload.guild_id, payload.message_id)
        if type == Util.ReactionType.UNKNOWN:
            return
        ReactionRoleUtil.__addRoleToUser(bot, payload.user_id, type)

    def removeReaction(payload: RawReactionClearEvent):
        pass

    def __findMessageRecord(guild_id: int, message_id: int) -> Util.ReactionType:
        query = ReactionMessage.select().where(ReactionMessage.guild_id == guild_id, ReactionMessage.message_id == message_id)
        if query.exists():
            reactionMsg: ReactionMessage = query.get()
            return Util.ReactionType(reactionMsg.message_type)
        return Util.ReactionType.UNKNOWN
    
    def __addRoleToUser(bot: commands.Bot, guild_id: int, user_id: int, type: Util.ReactionType):
        
        guild = get(lambda g: g.id == guild_id, bot.guilds)
        if not guild:
            return
        
        