from __future__ import unicode_literals
import youtube_dl
from apiclient.discovery import build
from apiclient.errors import HttpError
from google.cloud import storage
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
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

class PreParseNode(object):
    def __init__(self,youtbeUrl,videoID,title,transcript):
        self.videoID = videoID
        self.title = title
        self.youtbeUrl = youtbeUrl
        self.transcript = transcript


    def __repr__(self):
        pass



def uploadToGcp(filename):
    storage_client = storage.Client()
    bucket_to_use = storage_client.get_bucket('facebookglobalhackathon')
    blob = bucket_to_use.blob(filename)
    if not blob.exists():
        blob.upload_from_filename(filename)
    #return the file uri
    uri_base = "gs://facebookglobalhackathon/"
    uri = uri_base + filename
    return uri



def parseVideos(svideoLink:list,outputId):
    ydl_opts = {
          'format': 'bestaudio/best',
           'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
    }],
    'outtmpl': "%(id)s.%(ext)s",
    'logger': YouTubeDlLogger(),
    'progress_hooks': [my_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(svideoLink)

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
    itemsToParse = res['items']
    preParsedNodes = []
    for i in itemsToParse:
        title = i['snippet']['title']
        videoID = i['snippet']['resourceId']['videoId']
        youtubeUrl = "https://www.youtube.com/watch?v=" + videoID
        #parse the audio file
        parseVideos([youtubeUrl],videoID)
        uploadToGcp(videoID + ".mp3")
        preParsedNodes.append(PreParseNode(youtubeUrl,videoID,title,None))
    return preParsedNodes
getVideosGivenPlayList("PLfMspJ0TLR5HRFu2kLh3U4mvStMO8QURm")

