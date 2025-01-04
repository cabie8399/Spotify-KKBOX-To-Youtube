# 引入 requests 模組
import requests
from kkbox_client import token

import os
import time
import argparse

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.errors import HttpError


playlist = {'tracks': []}


def get_kkbox_playlist_tracks(kkbox_playlist_id):
    # url = "https://api.kkbox.com/v1.1/charts/{}/tracks?territory=TW".format(kkbox_playlist_id)
    url = "https://api.kkbox.com/v1.1/charts/{}/tracks?territory=TW&offset=0&limit=5".format(kkbox_playlist_id)
    auth = "Bearer {}".format(token)
    headers = {
        'accept': "application/json",
        'authorization': auth
    }

    # 使用 GET 方式下載普通網頁
    r = requests.get(url, headers = headers)
    res = r.json()

    # pprint.pprint(res)
    for i in res['data']:
        # pprint.pprint(i)
        print(i['name'], "-", i['album']['artist']['name'])
        track_name = i['name']
        main_artist = i['album']['artist']['name']
        track = {
            'name': track_name,
            'artist': main_artist
        }
        playlist['tracks'].append(track)

def get_youtube_client():
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # scopes = ["https://www.googleapis.com/auth/youtubepartner"]
        scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_local_server(port=0)
        youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
        return youtube

def get_youtube_video(youtube, track):
    query = "{} - {}".format(track['artist'], track['name'])
    request = youtube.search().list(
        part="snippet",
        q=query
    )
    response = request.execute()
    for item in response['items']:
        if item['id']['kind'] == 'youtube#video':

            video_title = item['snippet']['title']
            video_id = item['id']['videoId']
            print(video_title)
            break

    return video_id

def create_youtube_playlist(youtube, title, description=""):
    try:
        request = youtube.playlists().insert(
            part="snippet",
            body={
                "snippet": {
                    "title": title,
                    "description": description
                }
            }
        )
        response = request.execute()

        playlist_id = response['id']
        playlist_title = response['snippet']['localized']['title']
        print('-' * 30)
        print(playlist_title)
        print("https://www.youtube.com/playlist?list={}".format(playlist_id))
        print('-' * 30)

        return playlist_id
    except HttpError as err:
        print("ERROR CODE : ",err.resp.status)
        if err.resp.status in [403, 500, 503]:
            time.sleep(5)
        else: raise


def add_video_to_youtube_playlist(youtube, video_id, playlist_id):
    try:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                'snippet': {
                    'playlistId': playlist_id,
                    'resourceId': {
                        'kind': 'youtube#video',
                        'videoId': video_id
                    }
                }
            }
        )
        request.execute()
    except HttpError as err:
        print("ERROR CODE : ",err.resp.status)
        if err.resp.status in [409, 500, 503]:
            time.sleep(5)
        else: raise

def convert(kkbox_playlist_id, playlist_name):
    get_kkbox_playlist_tracks(kkbox_playlist_id)
    youtube = get_youtube_client()
    playlist_id = create_youtube_playlist(youtube, playlist_name, "kkbox")
    for track in playlist['tracks']:
        video_id = get_youtube_video(youtube, track)
        add_video_to_youtube_playlist(youtube, video_id, playlist_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kkbox_playlist_id', type=str)
    parser.add_argument('playlist_name')
    args = parser.parse_args()

    convert(args.kkbox_playlist_id, args.playlist_name)
    print("Finished")