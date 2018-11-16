from flask import Flask, request, json
import mongodb as mongo
import config

playListLink = ""



#This will change with more heuristics
def findBestSuggestion(suggestions):
    ret = {
        "videoID":suggestions[0]["videoID"],
        "timeStamp":suggestion[0]["timeStamp"][0]
    }
    return ret



@app.route('/setPlayList', methods=['POST'])
def setLink():
    if not request.json:
        abort(400)
    separate = request.json["playListLink"].split("&list=")
    if len(separate) != 2:
        abort(400)
    playListLink = separate[1]

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
