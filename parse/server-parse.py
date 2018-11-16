from flask import Flask, request, json
import mongodb as mongo
import config
from ParseVideo import *
from threading import Thread


playListLink = ""
app = Flask(__name__)


#This will change with more heuristics
def findBestSuggestion(suggestions):
    ret = {
        "videoID":suggestions[0]["videoID"],
        "timeStamp":suggestion[0]["timeStamp"][0]
    }
    return ret




@app.route('/setPlayList', methods=['POST'])
def setLink():
    t = Thread(target=getVideosGivenPlayList,args="PLD6cpMQHuQEQ-005myefm5J9oiXeBXRjJ",
        response.json["topic"].upper(), response.json["subtopic"])
    t.start()
    return {"status":200}
    #if not request.json:
    #    abort(400)
    #separate = request.json["playListLink"].split("&list=")
    #if len(separate) != 2:
    #    abort(400)
    #playListLink = separate[1]

@app.route('/checkProgress', methods=['GET'])

@app.route('/getVideo', methods=['POST'])
def getVideo():
    if not request.json and playListLink == "":
        abort(400)

    info = request.json
    topic = info['topic']
    subtopic = info['subtopic']
    videoIDs = mongo.getListVideos(topic)
    suggestions = []
    for videoID in videoIDs:
        suggestions.append(mongo.findSubTopic(topic,subtopic,videoID))
    bestSuggestion = findBestSuggestion(suggestions)
    ret = {
        "videoLink":mongo.getVideoLink(bestSuggestion["videoID"]),
        "timeStamp":bestSuggestion["timeStamp"]
    }
    return ret

if __name__ == "__main__":
    app.run(port=8080,host="0.0.0.0",debug=True)
