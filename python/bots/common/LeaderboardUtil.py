from common.models.EmojiTracker import EmojiTracker
from common.models.Emotion import Emotion
from common.models.Leaderboard import Leaderboard
from common.models.EmojiTracker import EmojiTracker

class LeaderboardUtil():
    
    # find leaderboard based on lb_name
    def getOrCreateLeaderboard(lb_name: str):
        query = Leaderboard.select().where(
            Leaderboard.name == lb_name.lower()
        )
        if not query.exists():
            Leaderboard.insert(name = lb_name.lower()).execute()    
        return query.get()
    
    # get or create emoji for leaderboard
    def getOrCreateEmoji(leaderboard: Leaderboard, emoji: str):
        query = Emotion.select().where(
            Emotion.leaderboard_id == leaderboard.id,
            Emotion.emoji == emoji
        )
        if not query.exists():
            Emotion.insert(leaderboard_id = leaderboard.id, emoji = emoji).execute()
        return query.get()
    
    def getOrCreateTracker(leaderboard_id: int, member_id: int, emotion_id: int):
        query = EmojiTracker.select().where(
            EmojiTracker.member_id == member_id,
            EmojiTracker.leaderboard_id == leaderboard_id,
            EmojiTracker.emotion_id == emotion_id
        )
        if not query.exists():
            EmojiTracker.insert(
                member_id = member_id, 
                leaderboard_id = leaderboard_id, 
                emotion_id = emotion_id, 
                count = 0).execute()
        return query.get()

    def getTracker(lb_id: int, emoji_id: int):
        query = EmojiTracker.select().where(
            EmojiTracker.leaderboard_id == lb_id,
            EmojiTracker.emotion_id == emoji_id
        )
        if query.exists():
            return query.get()
        return None
    
    def getAllTrackers(leaderboard_id: int, member_id: int):
        query = EmojiTracker.select().where(
            EmojiTracker.member_id == member_id,
            EmojiTracker.leaderboard_id == leaderboard_id,
        )
        result = []
        if query.exists():
            for tracker in query.iterator():
                result.append(tracker)
        return result
    
    def addEmoji(lb_name: str, emoji: str):
        leaderboard = LeaderboardUtil.getOrCreateLeaderboard(lb_name)
        return LeaderboardUtil.getOrCreateEmoji(leaderboard, emoji)

    def removeCategory(lb_name: str):
        leaderboard = LeaderboardUtil.findLeaderboard(lb_name)
        if not leaderboard:
            return
        emojis = LeaderboardUtil.__listEmojisWithLeaderboard(leaderboard)
        if emojis:
            for emoji in emojis:
                LeaderboardUtil.setRecord(leaderboard.id, emoji.id, 0)
                emoji.delete_instance()
        leaderboard.delete_instance()
        
    # remove emoji from leaderboard tracking
    def removeEmoji(lb_name: str, emoji: str):
        leaderboard = LeaderboardUtil.getOrCreateLeaderboard(lb_name)
        query = Emotion.select().where(
            Emotion.leaderboard_id == leaderboard.id,
            Emotion.emoji == emoji
        )
        e: Emotion
        if query.exists():
            e = query.get()
            e.delete_instance()
        return True

    def listLeaderboards():
        query = Leaderboard.select()
        result = []
        if query.exists():
            for leaderboard in query.iterator():
                result.append(leaderboard)
        return result
    
    # list all emoji a leaderboard is tracking
    def listEmojis(lb_name: str):
        leaderboard = LeaderboardUtil.getOrCreateLeaderboard(lb_name)
        return LeaderboardUtil.__listEmojisWithLeaderboard(leaderboard)
    
    def __listEmojisWithLeaderboard(leaderboard: Leaderboard):
        result = []
        query = Emotion.select().where(Emotion.leaderboard_id == leaderboard.id)
        if query.exists():
            for emoji in query.iterator():
                result.append(emoji)
        return result
    
    def findLeaderboard(lb_name: str):
        query = Leaderboard.select().where(
            Leaderboard.name == lb_name.lower()
        )
        if query.exists():
            return query.get()
        return None

    def findLeaderboardById(lb_id: int):
        query = Leaderboard.select().where(
            Leaderboard.id == lb_id
        )
        if query.exists():
            return query.get()
        return None

    def findEmoji(emoji: str):
        query = Emotion.select().where(
            Emotion.emoji == emoji
        )
        if query.exists():
           return query.get()
        return None
    
    def updateTracker(leaderboard_id: int, member_id: int, emotion_id: int, count: int):
        tracker = LeaderboardUtil.getOrCreateTracker(leaderboard_id, member_id, emotion_id)
        tracker.count = max(tracker.count + count, 0)
        tracker.save()
    
    def __addReactionCount(member_id: int, emoji: str, count: int):
        e: Emotion = LeaderboardUtil.findEmoji(emoji)
        if e:
            LeaderboardUtil.updateTracker(e.leaderboard_id, member_id, e.id, count)
            
    def addReaction(member_id: int, emoji: str):
        LeaderboardUtil.__addReactionCount(member_id, emoji, 1)

    def removeReaction(member_id: int, emoji: str):
        LeaderboardUtil.__addReactionCount(member_id, emoji, -1)
    
    def getTotalReactionCounts(leaderboard_id: int, member_id: int):
        trackers = LeaderboardUtil.getAllTrackers(leaderboard_id, member_id)
        total = 0
        for tracker in trackers:
            total += tracker.count
        return total
        
     # clear leaderboard count records
    def setRecord(lb_id: int, emoji_id: int, count: int):
        tracker = LeaderboardUtil.getTracker(lb_id, emoji_id)
        tracker.count = max(count, 0)
        tracker.save()

    def getRankResult(lb_name: str):
        lb = LeaderboardUtil.findLeaderboard(lb_name)
        if not lb:
            return None
        query = EmojiTracker.select().where(
            EmojiTracker.leaderboard_id == lb.id
        )

        if query.exists():
            result = {}
            trackers = query.iterator()
            for tracker in trackers:
                key = tracker.member_id
                if key in result:
                    result[key] += tracker.count
                    print(f"new count {result[key]}")
                else:
                    if tracker.count > 0:
                        result.update({key: tracker.count})
            return result
        return None
    