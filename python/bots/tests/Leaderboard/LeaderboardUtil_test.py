from common.LeaderboardUtil import LeaderboardUtil
from common.KFP_DB import KfpDb

class TestLeaderboardUtil():
    def setup_method(self, method):
        self.database = KfpDb(":memory:")
        
    def teardown_method(self, method):
        self.database.teardown()
        
    def test_createLeaderboard(self):
        leaderboard = LeaderboardUtil.getOrCreateLeaderboard("Test Name")
        assert leaderboard.name == "test name"
    
    def test_getLeaderboard(self):
        leaderboard = LeaderboardUtil.getOrCreateLeaderboard("does not exist")
        assert leaderboard.name == "does not exist"
        
    def test_addEmojiToLeaderboard(self):
        emoji = LeaderboardUtil.addEmoji("hello", ":emoji:")
        assert emoji.emoji == ":emoji:"
        
        result = LeaderboardUtil.listEmojis("hello")
        assert len(result) == 1
        assert result[0].emoji == ":emoji:"
        
    def test_addMultipleEmojiToLeaderboard(self):
        emoji1 = LeaderboardUtil.addEmoji("hello", "emoji1")
        emoji2 = LeaderboardUtil.addEmoji("hello", "emoji2")
        
        result = LeaderboardUtil.listEmojis("hello")
        assert len(result) == 2
        assert result[0] == emoji1
        assert result[1] == emoji2
        
    def test_removeEmojiFromLeaderboard(self):
        emoji1 = LeaderboardUtil.addEmoji("hello", "emoji1")
        emoji2 = LeaderboardUtil.addEmoji("hello", "emoji2")
        
        result = LeaderboardUtil.removeEmoji("hello", "emoji1")
        result = LeaderboardUtil.listEmojis("hello")
        assert len(result) == 1
        assert result[0] == emoji2
        
    def test_addRecordToLeaderboard(self):
        emoji1 = LeaderboardUtil.addEmoji("hello", "emoji1")
        
        LeaderboardUtil.addReaction(123, "emoji1")
        
        assert LeaderboardUtil.getReactionCount(emoji1.leaderboard_id, 123) == 1
        
    def test_addRecordMultipleToLeaderboard(self):
        emoji1 = LeaderboardUtil.addEmoji("hello", "emoji1")
        
        LeaderboardUtil.addReaction(123, "emoji1")
        LeaderboardUtil.addReaction(123, "emoji1")
        
        assert LeaderboardUtil.getReactionCount(emoji1.leaderboard_id, 123) == 2
    
    def test_addRecordToMultiEmojiLeaderboard(self):
        emoji1 = LeaderboardUtil.addEmoji("hello", "emoji1")
        emoji1 = LeaderboardUtil.addEmoji("hello", "emoji2")
        
        LeaderboardUtil.addReaction(123, "emoji1")
        LeaderboardUtil.addReaction(123, "emoji1")
        LeaderboardUtil.addReaction(123, "emoji2")
        
        assert LeaderboardUtil.getTotalReactionCounts(emoji1.leaderboard_id, 123) == 3