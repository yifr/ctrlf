from flask import Flask, request, json, jsonify
import mongodb as mongo
import config
from ParseVideo import *
from threading import Thread


playListLink = ""
app = Flask(__name__)


@app.route('/setPlayList', methods=['POST'])
def setLink():
    t = Thread(target=getVideosGivenPlayList,args=("PLD6cpMQHuQEQ-005myefm5J9oiXeBXRjJ",request.json["topic"].upper(), request.json["subtopic"]))
    t.start()
    return jsonify({"staus":200})
    #if not request.json:
    #    abort(400)
    #separate = request.json["playListLink"].split("&list=")
    #if len(separate) != 2:
    #    abort(400)
    #playListLink = separate[1]

@app.route('/searchSubtopic', methods=['GET'])
def searchSub():

    if not request.json["topic"] or not request.json["subtopic"]:
        return jsonify({"status":400})
    topic = request.json["topic"].upper().replace(" ","_")
    suggestions = mongo.find(topic, request.json["subtopic"])
    timeStamps = suggestions[0][1][1][0]["timeStamp"]
    for i in range(0,len(timeStamps)):
        preParsedTs = "%0.2f" % (timeStamps[i] / 60)
        timeStamps[i] = float(preParsedTs)


    ret = {
        "videoLink":suggestions[0][0],
        "timeStamps":timeStamps
    }
    return jsonify(ret)



if __name__ == "__main__":
    app.run(port=6969,host="0.0.0.0",debug=True)
