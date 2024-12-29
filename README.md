# Spotify To YouTube

- TODO : 亂亂寫，架構未整理，但功能正常

# Usage

- 參考[Spotify Web API](https://developer.spotify.com/documentation/web-api/)設定，將ID跟Secret貼到`secrets.py` 
- 設置環境變數 : 後面帶自己的ID跟SECRET(以下只是示範，只是亂碼)
```
export SPOTIPY_CLIENT_ID='e61780fe758ee7axxxxxxxxxx'
export SPOTIPY_CLIENT_SECRET='391751d448xxxxxxxxxxx'
```

- 參考Google OAuth設定，開啟[Youtube Data API v3](https://developers.google.com/youtube/v3/)，並下載client_secrets.json


- 進入虛擬環境
```
python -m venv venv
source ./venv/bin/activate

pip install -r requirements.txt
```

- 執行，並後面代上spotify playlist 的 ID
(https://open.spotify.com/playlist/22XNgsUg5DFG9nqGAYtE0B)，以及想在YT建立的新播放清單名字
```
python convert_playlist.py 22XNgsUg5DFG9nqGAYtE0B New_Playlist_Name
```
- 複製播放清單完成

<br><br>


# 參考
- [spotipy-Github](https://github.com/spotipy-dev/spotipy/tree/master)
- [spotipy-DOC](https://spotipy.readthedocs.io/en/2.24.0/)
- [Python - 數位行銷分析與 Youtube API 教學](https://ithelp.ithome.com.tw/users/20140740/ironman/4250?page=1)