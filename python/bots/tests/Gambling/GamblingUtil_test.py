from common.KFP_DB import KfpDb
from common.Util import Util
from common.models.GamblingGame import GamblingGame
from common.GamblingUtil import GamblingUtil

class TestGamblingUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")
        pass
    def teardown_method(self, method):
        pass

    def test_gameCreation(self):
        game:GamblingGame = GamblingUtil.create_game(123, "new_game", 5, ["hello", "hi"], 123)

        assert game.guild_id == 123
        assert game.name == "new_game"
        assert game.base == 5
        assert game.pool == 0
        assert game.item_list == ["hello", "hi"]
        assert game.creater_id == 123
        assert game.status == Util.GamblingStatus.init

    def test_updateGameStatus(self):
        game:GamblingGame = GamblingUtil.create_game(123, "new_game", 5, ["hello", "hi"], 123)
        GamblingUtil.update_game_status(game, Util.GamblingStatus.ready, 123, 456)
        result_game = GamblingUtil.get_game(game.id)

        assert game == result_game

    def test_getActiveGameList(self):
        game1:GamblingGame = GamblingUtil.create_game(123, "new_game1", 5, ["hello", "hi"], 123)        
        game2:GamblingGame = GamblingUtil.create_game(123, "new_game2", 5, ["hello", "hi"], 123)        
        gameList = GamblingUtil.get_active_games(123)
        assert len(gameList) == 0

        GamblingUtil.update_game_status(game1, Util.GamblingStatus.ready, 123, 321)
        gameList = GamblingUtil.get_active_games(123)
        assert len(gameList) == 1

        GamblingUtil.update_game_status(game2, Util.GamblingStatus.ready, 123, 321)
        gameList = GamblingUtil.get_active_games(123)
        assert len(gameList) == 2
        assert gameList == [game1, game2]

    def test_getActiveGameInChannel(self):
        original:GamblingGame = GamblingUtil.create_game(123, "new_game", 5, ["hello", "hi"], 123)
        GamblingUtil.update_game_status(original, Util.GamblingStatus.ready, 123, 456)

        game = GamblingUtil.get_active_game_in_channel(123, 456)
        assert len(game) == 0
        game = GamblingUtil.get_active_game_in_channel(123, 123)
        assert game == [original]

        another = GamblingUtil.create_game(123, "new_game", 5, ["hello", "hi"], 123)
        GamblingUtil.update_game_status(another, Util.GamblingStatus.ready, 123, 456)
        game = GamblingUtil.get_active_game_in_channel(123, 123)
        assert len(game) == 2

    def test_addBetFailedNotReady(self):
        original:GamblingGame = GamblingUtil.create_game(123, "new_game", 5, ["hello", "hi"], 123)
        assert not GamblingUtil.add_bet(original, 123, 2, 1)

    def test_addBetSuccess(self):
        original:GamblingGame = GamblingUtil.create_game(123, "new_game", 5, ["hello", "hi"], 123)
        GamblingUtil.update_game_status(original, Util.GamblingStatus.ready, 123, 456)
        assert GamblingUtil.add_bet(original, 123, 10, 1)

        original:GamblingGame = GamblingUtil.get_game(original.id)
        assert original.pool == 10

        assert GamblingUtil.add_bet(original, 123, 10, 1)
        assert original.pool == 20

    def test_getBets(self):
        original:GamblingGame = GamblingUtil.create_game(123, "new_game", 5, ["hello", "hi"], 123)
        GamblingUtil.update_game_status(original, Util.GamblingStatus.ready, 123, 456)
        assert GamblingUtil.add_bet(original, 123, 10, 1)
        
        bets = GamblingUtil.get_bets(original)
        assert len(bets) == 1

    def test_addGamePoolAmount(self):
        original:GamblingGame = GamblingUtil.create_game(123, "new_game", 5, ["hello", "hi"], 123)
        GamblingUtil.add_game_pool_amount(original, 300)
        original = GamblingUtil.get_game(original.id)

        assert original.pool == 300
        
