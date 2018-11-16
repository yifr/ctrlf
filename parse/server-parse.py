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
    requestID = str(mongo.uuid.uuid4())
    suggestions = mongo.find(request.json["topic"].upper(), request.json["subtopic"])
    ret = {
        "videoLink":suggestions[0][0],
        "timeStamps":suggestions[0][1]
    }
    return jsonify(ret)



if __name__ == "__main__":
    app.run(port=6969,host="0.0.0.0",debug=True)
