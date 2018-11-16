from pymongo import MongoClient
import config
import uuid



#REMINDERS
#1. topics are UPPERCASE and use - instead of spaces
#2. subtopics are lowercase


client = None


class TreeNode(object):
    videoID = ""
    timeStamp = []
    children = []
    letter = ''
    treeID = ""
    parent = ""


    def __init__(self, videoID,parent,letter):
        self.videoID = videoID
        self.timeStamp = []
        this.children = [None for i in range(0,25)]
        this.treeID = uuid.uuid4()
        this.parent = parent
        this.letter = letter



def getFromCache(topic:str,subtopic:str):
    if client == None:
        print("CLIENT IS NONE!")
    collection = client['meta']['cache']
    document = collection.find_one({"topic":topic})
    return document

def isSubtopicCached(topic:str,subtopic:str):
    if client == None:
        print("CLIENT IS NONE!")
    if not containsTopic(topic):
        return False

    document = getFromCache(topic,subtopic)
    if subtopic in document["subtopics"]:
        return True
    return False

def getCachedSubTopic(topic:str,subtopic:str):
    if client == None:
        print("CLIENT IS NONE!")
    result = {}
    if not isSubtopicCached:
        return None

    document = getFromCache(topic,subtopic)
    suggestions = document["subtopics"][suggestions]
    return suggestions


def insertTopic(topic:str,transcripts:list,videoID:str,videoLink:str):
    if client == None:
        print("CLIENT IS NONE!")
    collection = client["topics"][topic]
    insertTree(buildTree(transcripts))
    client["meta"]["videoLinks"].insert_one({"videoID":videoID,"videoLink":videoLink})


def findSubTopic(topic:str,subtopic:str,videoID:str):
    if(isSubtopicCached(topic,subtopic)):
        return getCachedSubTopic(topic,subtopic)
    subtopicWords = subtopic.split(" ")
    suggestions = []
    for i in range(0,size(subtopicWords)):
        subtopic = subtopicWords[i]
        rootDoc = client["topics"][topic].find_one({"videoID":videoID,"parent":None})
        if rootDoc == None:
            return rootDoc
        parent = rootDoc["treeID"]
        i = 0
        curDoc = None
        while i < len(subtopic):
            curDoc = client["topics"][topic].find_one({"videoID":videoID,"parent":parent,"letter":char(subtopic[i]}))
            if curDoc == None:
                break
            parent = curDoc["treeID"]
            i+=1
        suggestions.append(curDoc)
    return suggestions






def insertTree(topic:str,root:TreeNode):
    if client == None:
        print("CLIENT IS NONE!")
    post = {
        "videoID":root.videoID,
        "timeStamp":root.timeStamp,
        "treeID":root.treeID,
        "parent":root.parent,
        "letter":root.letter
    }
    client["topics"][topic].insert_one(post)
    for i in range(0,25):
        if root[i] != None:
            insertTree(topic,root[i])

#TO-DO: Need to see how transcripts look like
def buildTree(transcripts:list):


def insertWord(root:TreeNode,word:str,timeStamp:str,i:int):
    if client == None:
        print("CLIENT IS NONE!")
    if i == len(word):
        root.timeStamp.append(timeStamp)
    if root.children[ord(word[i])-ord('a')] == None:
        root.children[ord(word[i])-ord('a')] = TreeNode(root.videoID,root.treeID,char(word[i]))
    insertWord(root.children[ord(word[i])],word,timeStamp,i+=1)



def removeTree(videoID:str):
    pass

def connect():
    global client
    client = pymongo.MongoClient("mongodb://azoam:"+config.MongoPass+
    "@cluster0-shard-00-00-r9vk0.gcp.mongodb.net:27017,cluster0-shard-"+
    "00-01-r9vk0.gcp.mongodb.net:27017,cluster0-shard-00-02-r9vk0.gcp."+
    "mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")