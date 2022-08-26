from datetime import datetime
from .models.RouletteGameBet import RouletteGameBet
from .models.RouletteGame import RouletteGame

class RouletteUtil():
    
    # try to start a game, return channel id if a game already on going
    def startGame(guild_id: int, channel_id: int):
        game = RouletteUtil._getExistingGame(guild_id)
        if game != None:
            return game.channel_id
        else:
            game = RouletteUtil._createGame(guild_id, channel_id)
            return None
    
    # find game that times are up and waiting to be concluded
    def findUnConcludedGame(guild_id: int):
        return RouletteUtil._getExpiredGame(guild_id)
    
    # mark unconcluded game finished, and return game id
    def concludeGame(guild_id: int, winning_number: int):
        game = RouletteUtil.findUnConcludedGame(guild_id)
        if game != None:
            game.winning_number = winning_number
            game.save()
            return game.id
        else:
            return None
    
    # try to place a bet to current game, return channel id if channel is incorrect. Return -1 if no existing game
    def placeBet(guild_id: int, channel_id: int, member_id: int, amount: int):
        game = RouletteUtil._getExistingGame(guild_id)
        if game == None:
            return -1
        elif game.channel_id != channel_id:
            return game.channel_id
        else:
            RouletteUtil._createBet(game.id, guild_id, member_id, amount)
            return 0
        
    def getWinners(game_id: int, winning_number: int):
        winners = []
        query = RouletteGameBet.select().where(
            RouletteGameBet.game_id == game_id,
            RouletteGameBet.betting_number == winning_number
        )
        if query.exists():
            for bet in query.iterator():
                winners.append(bet)
        return winners
        
    def _createBet(game_id: int, member_id: int, amount: int):
        RouletteGameBet.insert(
            game_id = game_id,
            member_id = member_id,
            amount = amount,
        ).execute()
        
    def _getExpiredGame(guild_id: int):
        now = datetime.now()
        query = RouletteGame.select().where(
            RouletteGame.guild_id == guild_id,
            RouletteGame.expire_time >= now,
            RouletteGame.winning_number == -1
        )
        if query.exists():
            game: RouletteGame = query.get()
            return game
        else:
            return None
    
    def _getExistingGame(guild_id: int):
        now = datetime.now()
        query = RouletteGame.select().where(
            RouletteGame.guild_id == guild_id,
            RouletteGame.expire_time < now,
            RouletteGame.winning_number == -1
        )
        if query.exists():
            game: RouletteGame = query.get()
            return game
        else:
            return None