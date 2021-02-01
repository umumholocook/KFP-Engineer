import tweepy

consumer_key = 'API key'
consumer_secret = 'API secret'
access_token = 'Access token'
access_secret = 'Access Secret'
count = 3 # <- 一次要多少個推文
screenname = "takanashikiara" # <- 想抓的推特帳號

authentication = tweepy.OAuthHandler(consumer_key, consumer_secret)
authentication.set_access_token(access_token, access_secret)
api = tweepy.API(authentication, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

tweets = api.user_timeline(screenname, count = count)

for tweet in tweets:
    print(tweet.text, end = "\n")
    for entity in tweet.entities: # 通常圖片url是放在 entities裡面
        print("\t", entity, end = "\n")
    print("\n\n")
