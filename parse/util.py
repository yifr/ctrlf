class PreParseNode(object):
    videoID = ""
    title = ""
    youtubeUrl = ""
    transcript = []

    def __init__(self,youtubeUrl,videoID,title,transcript):
        self.youtubeUrl = youtubeUrl
        self.videoID = videoID
        self.title = title
        self.transcript = transcript