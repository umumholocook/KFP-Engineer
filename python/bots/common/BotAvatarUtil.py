# This bot avatar will lookup Twitter account and use their avatar

import os
import tempfile

import requests

twitter_token = os.environ.get("KFP_TWITTER_BEARER_TOKEN")

# Update this method if Twitter api changed
def __parseResultData(dict):
    image_url = dict["data"][0]["profile_image_url"]
    return image_url.replace("_normal.", ".")

def fetchUserAvatarUrl():
    if not twitter_token:
        print("Twitter token is not set, ignore avatar setting")
        return

    result = __parseResultData(connect_to_endpoint(create_url()))
    
    if not result:
        print("Error on loading twitter avatar url, possibly due to change of API.")
        return
    
    if not __shouldRedownloadImage(result):
        print("Image is the same as previous check, ignore")
        return
    else:
        __updateLastImageUrlCache(result)

    return result

def oauth(r):
    # authentication
    r.headers["Authorization"] = f"Bearer {twitter_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r

def create_url():
    usernames = "usernames=takanashikiara"
    user_fields = "user.fields=profile_image_url"
    url = "https://api.twitter.com/2/users/by?{}&{}&scope=users.read".format(usernames, user_fields)
    return url

def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=oauth,)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def downloadImage(url: str):
    if not url.endswith(".jpg"):
        print("Avator has image that's not jpg, abandon download image for now")
        return
    response = requests.request("GET", url)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    imageFilePath = getBotAvatarImageFilePath()
    if os.path.exists(imageFilePath):
        # clear old data
        os.remove(imageFilePath)
    # save new data
    with open(imageFilePath, 'wb') as handler:
        handler.write(response.content)

def getBotAvatarImageFilePath():
    return os.sep.join((tempfile.gettempdir(), "bot_avatar.jpg"))

def __updateLastImageUrlCache(newUrl: str):
    cachePath = __getLastImageUrlCacheFilePath()

    if os.path.exists(cachePath):
        os.remove(cachePath)
    
    with open(cachePath, 'w') as handler:
        handler.write(newUrl)

def __shouldRedownloadImage(url: str):
    print(__getLastImageUrl())
    return url != __getLastImageUrl()

def __getLastImageUrl(): 
    cachePath = __getLastImageUrlCacheFilePath()
    if not os.path.exists(cachePath):
        return ""
    
    with open(__getLastImageUrlCacheFilePath()) as f:
        return f.readlines()[0]

def __getLastImageUrlCacheFilePath():
    return os.sep.join((tempfile.gettempdir(), "bot_avatar_cache.txt"))
