import tweepy

consumer_key = 'API key'
consumer_secret = 'API secret'
access_token = 'Access token'
access_secret = 'Access Secret'
tweetsPerQry = 100
maxTweets = 1000000
hashtag = "#mencatatindonesia" # <- 想搜的hashtag

authentication = tweepy.OAuthHandler(consumer_key, consumer_secret)
authentication.set_access_token(access_token, access_secret)
api = tweepy.API(authentication, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
maxId = -1
tweetCount = 0
while tweetCount < maxTweets:
	if(maxId <= 0):
		newTweets = api.search(q=hashtag, count=tweetsPerQry, result_type="recent", tweet_mode="extended")
	else:
		newTweets = api.search(q=hashtag, count=tweetsPerQry, max_id=str(maxId - 1), result_type="recent", tweet_mode="extended")

	if not newTweets:
		print("Tweet Habis")
		break
	
	for tweet in newTweets:
		# 在這邊加入想要過濾掉的推特邏輯
		print(tweet.full_text.encode('utf-8'))
		
	tweetCount += len(newTweets)	
	maxId = newTweets[-1].id
