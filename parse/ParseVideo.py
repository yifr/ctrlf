from __future__ import unicode_literals
import youtube_dl
from apiclient.discovery import build
from apiclient.errors import HttpError
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
import config
class YouTubeDlLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'logger': YouTubeDlLogger(),
    'progress_hooks': [my_hook],
}
def getVideosGivenPlayList(playListID:str):
    #build youtube client
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION,
                    developerKey=config.YOUTUBE_API_KEY)
    res = youtube.playlistItems().list(
        part="snippet",
        playlistId=playListID,
        maxResults="50"
    ).execute()
    print(res['items'])

getVideosGivenPlayList("PLfMspJ0TLR5HRFu2kLh3U4mvStMO8QURm")






def parseVideos(svideoLink:list):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(svideoLink)
