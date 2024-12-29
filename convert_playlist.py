# pylint: disable=line-too-long

import os
import time
import argparse
import requests
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.errors import HttpError

class ConvertPlaylist():

    def __init__(self):
        self.youtube = self.get_youtube_client()
        self.playlist = {'tracks': []}

    def get_spotify_song(self, track):
        query = f"https://api.spotify.com/v1/search?query=track%3A{track['name']}+artist%3A{track['artist']}&type=track&offset=0&limit=20"
        response = requests.get(
            query,
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer {}"
            }
            ,timeout=10
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        uri = songs[0]["uri"]

        return uri

    def get_spotify_playlist(self, spotify_uri):
        playlist_id = spotify_uri
        client_credentials_manager = SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        response_json = sp.playlist(playlist_id)
        self.playlist['title'] = response_json['name']
        self.playlist['description'] = response_json['description']
        items = response_json['tracks']['items']
        for item in items:
            track_name = item['track']['name']
            main_artist = item['track']['artists'][0]['name']
            track = {'name': track_name,
                     'artist': main_artist}
            self.playlist['tracks'].append(track)

    def get_youtube_client(self):
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

    def get_youtube_video(self, track):
        query = "{} - {}".format(track['artist'], track['name'])
        request = self.youtube.search().list(
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

    def create_youtube_playlist(self, title, description=""):
        try:
            request = self.youtube.playlists().insert(
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


    def add_video_to_youtube_playlist(self, video_id, playlist_id):
        try:
            request = self.youtube.playlistItems().insert(
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

    def convert(self, spotify_uri, playlist_name):
        self.get_spotify_playlist(spotify_uri)
        playlist_id = self.create_youtube_playlist(playlist_name, self.playlist['description'])
        for track in self.playlist['tracks']:
            video_id = self.get_youtube_video(track)
            self.add_video_to_youtube_playlist(video_id, playlist_id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('spotify_uri', type=str)
    parser.add_argument('playlist_name')
    args = parser.parse_args()

    cp = ConvertPlaylist()
    cp.convert(args.spotify_uri, args.playlist_name)
    print("Finished")
