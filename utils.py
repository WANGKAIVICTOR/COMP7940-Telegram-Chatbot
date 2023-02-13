import os
import json
import configparser
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

def test(text):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    developerKey = config["YOUTUBE"]["DEVELOPER_KEY"]

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=developerKey)
    request = youtube.search().list(
        part="snippet",
        q=text,
    )
    response = request.execute()

    print("https://youtube.com/v/" + response["items"][0]["id"]["videoId"])
    return "https://youtube.com/v/" + response["items"][0]["id"]["videoId"]

if __name__ == "__main__":
    test("nb")