import random
from datetime import datetime, timedelta

from .models.RouletteGameBet import RouletteGameBet
from .models.RouletteGame import RouletteGame


class RouletteUtil():
    VALID_NUMBERS = [1, 3, 5, 10, 20]
    PAYOUT_MULTIPLIERS = {1: 2, 3: 4, 5: 6, 10: 12, 20: 25}
    GAME_DURATION_SECONDS = 40

    # try to start a game, return channel id if a game already on going
    def startGame(guild_id: int, channel_id: int):
        game = RouletteUtil._getExistingGame(guild_id)
        if game is not None:
            return game.channel_id
        RouletteUtil._createGame(guild_id, channel_id)
        return None

    def findUnConcludedGame(guild_id: int):
        return RouletteUtil._getExpiredGame(guild_id)

    def concludeGame(guild_id: int, winning_number: int):
        game = RouletteUtil.findUnConcludedGame(guild_id)
        if game is not None:
            game.winning_number = winning_number
            game.save()
            return game.id
        return None

    def placeBet(guild_id: int, channel_id: int, member_id: int, betting_number: int, amount: int):
        game = RouletteUtil._getExistingGame(guild_id)
        if game is None:
            return -1
        if game.channel_id != channel_id:
            return game.channel_id
        RouletteUtil._createBet(game.id, member_id, betting_number, amount)
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

    def generateWinningNumber():
        return random.choice(RouletteUtil.VALID_NUMBERS)

    def getPayoutMultiplier(number: int) -> int:
        return RouletteUtil.PAYOUT_MULTIPLIERS.get(number, 0)

    def _createGame(guild_id: int, channel_id: int):
        expire_time = datetime.now() + timedelta(seconds=RouletteUtil.GAME_DURATION_SECONDS)
        RouletteGame.create(
            guild_id=guild_id,
            channel_id=channel_id,
            expire_time=expire_time,
            winning_number=-1,
        )

    def _createBet(game_id: int, member_id: int, betting_number: int, amount: int):
        RouletteGameBet.insert(
            game_id=game_id,
            member_id=member_id,
            betting_number=betting_number,
            amount=amount,
        ).execute()

    def _getExpiredGame(guild_id: int):
        now = datetime.now()
        query = RouletteGame.select().where(
            RouletteGame.guild_id == guild_id,
            RouletteGame.expire_time <= now,
            RouletteGame.winning_number == -1
        )
        if query.exists():
            game: RouletteGame = query.get()
            return game
        return None

    def _getExistingGame(guild_id: int):
        now = datetime.now()
        query = RouletteGame.select().where(
            RouletteGame.guild_id == guild_id,
            RouletteGame.expire_time > now,
            RouletteGame.winning_number == -1
        )
        if query.exists():
            game: RouletteGame = query.get()
            return game
        return None