import os
import json
import configparser
import googleapiclient.discovery
import googleapiclient.errors

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')


def ytb_search(text):
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    if os.getenv('AM_I_IN_A_DOCKER_CONTAINER'):
        developerKey = os.getenv('DEVELOPER_KEY')
    else:
        developerKey = config["YOUTUBE"]["DEVELOPER_KEY"]

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=developerKey)
    request = youtube.search().list(
        part="snippet",
        q=text,
    )
    response = request.execute()
    # print(json.dumps(response))
    try:
        ret_dict = {ii["snippet"]["title"]: "https://youtube.com/v/" + ii["id"]["videoId"]
                    for ii in response["items"]}
        # print(ret_dict.keys())
        return ret_dict
    except Exception as e:
        return "换个关键词吧！"


if __name__ == "__main__":
    ytb_search("beef")
