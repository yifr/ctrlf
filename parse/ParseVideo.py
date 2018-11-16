from __future__ import unicode_literals
import youtube_dl
from apiclient.discovery import build
from apiclient.errors import HttpError
from google.cloud import storage
from google.cloud import speech
from google.cloud.speech import enums
import os
import io
from google.cloud.speech import types
import subprocess
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
import config
max_timestamp = 0

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







def extract(input_filename):
    print(input_filename)
    
    command = "ffmpeg -i " + input_filename + " -ab 160k -ac 1 -ar 16000 -vn "  + input_filename[0:len(input_filename) -3] + ".flac"
    subprocess.call(command, shell=True)



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

def transcribe_gcs():
    global max_timestamp
    client = speech.SpeechClient()
    files = sorted(os.listdir('parts/'))
    json_arr = []
    for f in files:
        name = "parts/" + f
        if('mp3' in name):
            extract(name)
            real_name = name[0:len(name)-3] + ".flac"
            os.remove(name)
            with io.open(real_name, 'rb') as audio_file:
        
                json_ret = {}
                content = audio_file.read()

                audio = types.RecognitionAudio(content=content)
                config = types.RecognitionConfig(
                     encoding=enums.RecognitionConfig.AudioEncoding.FLAC,
                        sample_rate_hertz=16000,
                        language_code='en-US',
                    enable_word_time_offsets=True
                    )

                response = client.recognize(config, audio)
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
                for result in response.results:
                    alternative = result.alternatives[0]
        # The first alternative is the most likely one for this portion.
                    print(u'Transcript: {}'.format(result.alternatives[0].transcript))   
                    for i in range(len(alternative.words)):
                         word_info = alternative.words[i]
                         word = word_info.word
                        
                         start_time = word_info.start_time
                         end_time = word_info.end_time
                         json_ret['word'] = word
                         json_ret['start_time'] = start_time.seconds + start_time.nanos * 1e-9 + max_timestamp
                         json_ret['end_time'] = end_time.seconds + end_time.nanos * 1e-9 + max_timestamp
                         json_arr.append(json_ret)
                         if(i == len(alternative.words)-1):
                             #update max
                             max_timestamp = json_ret['end_time']
            os.remove(real_name)

                    

def splitAudio(bigAudio):
    command =  "ffmpeg -i  " + bigAudio + " -f segment -segment_time 30 -c copy parts/out%03d.mp3"
    subprocess.call(command,shell=True)

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
        #convert mp3 to flac
       
        #uri = uploadToGcp("out.flac")
        #split the audiio file
        splitAudio(videoID +".mp3")
        ret = transcribe_gcs()
        print(ret)
        preParsedNodes.append(PreParseNode(youtubeUrl,videoID,title,ret))
    return preParsedNodes



getVideosGivenPlayList("PLfMspJ0TLR5HRFu2kLh3U4mvStMO8QURm")

