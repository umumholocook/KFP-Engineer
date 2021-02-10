import discord
from discord import Guild, Role, Member, Client
from discord.ext import commands
from common.KFP_DB import KfpDb

def load_json_file(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as fp:
            j = json.load(fp)
            fp.close()
            return j
    else:
        return False

class NewProfile(commands.Cog):

    db = None

    def __init__(self, client, dbFile:str):
        self.bot = client
        self.db = KfpDb(dbFile)
    
    @commands.Cog.listener('on_guild_join')
    async def profile_guild_join(self, guild:Guild):
        members = guild.members
        member_ids = []
        for member in members:
            if member.id == self.bot.user.id or member.bot:
                continue
            member_ids.append(member.id)
        self.db.add_members(member_ids)

def setup(client):
    # client.add_cog(NewProfile(client))
    pass