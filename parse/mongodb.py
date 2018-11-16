from pymongo import MongoClient
import config
import uuid
from util import PreParseNode
import re



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
        self.children = [None for i in range(0,25)]
        self.treeID = uuid.uuid4()
        self.parent = parent
        self.letter = letter



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
    insertTree(buildTree(transcripts,videoID))
    client["meta"]["videoLinks"].insert_one({"videoID":videoID,"videoLink":videoLink})


#Find the difference between the timestamps
def diffTime(timeStamp1,timeStamp2):
    return 0

def computeChains(suggestions:list):
    chains = [[suggestion[0]["timeStamp"][i]] for i in range(0,size(suggestion[0]["timeStamp"]))]
    finished = {}
    for i in range(1,size(suggestions)):
        for chain in chains:
            for timeStamp in suggestions[i]["timeStamp"]:
                if diffTime(chain[size(chain)-1],timeStamp) <= 1 and chain not in finished:
                    chain.append(timeStamp)
                    finished[chain] = True
            if len(chain) != i+1:
                chain = None
            finished = {}
    word = 0
    for suggestion in suggestions:
        suggestion["timeStamp"] = []
        for i in range(0,size(chains[word])):
            suggestion["timeStamp"].append(chains[i][word])
        word += 1



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
            curDoc = client["topics"][topic].find_one({"videoID":videoID,"parent":parent,"letter":subtopic[i]})
            if curDoc == None:
                break
            parent = curDoc["treeID"]
            i+=1
        if curDoc != None:
            suggestions.append(curDoc)
        else:
            break
    if size(subtopicWords) > 1:
        computeChains(suggestions)
    return suggestions


def getListVideos(topic:str):
    return client["topics"][topic].find().distinct("videoID")

def getVideoLink(videoID:str):
    return client["meta"]["videoLinks"].find({"videoID":videoID})["videoLink"]

def extractSymbols(word):
    return re.sub(r'[^\w]', ' ', word)

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
        if root.children[i] != None:
            insertTree(topic,root.children[i])

#TO-DO: Need to see how transcripts look like
def buildTree(transcripts:list,videoID:str):
    root = TreeNode(videoID,None,None)
    for word in transcripts:
        cleanWord = extractSymbols(word["word"]).lower()
        insertWord(root,cleanWord,word["start_time"],-1)
    return root


def insertWord(root:TreeNode,word:str,timeStamp:str,i:int):
    if i == len(word):
        root.timeStamp.append(timeStamp)
    if root.children[ord(word[i])-ord('a')] == None:
        root.children[ord(word[i])-ord('a')] = TreeNode(root.videoID,root.treeID,word[i])
    insertWord(root.children[ord(word[i])-ord('a')],word,timeStamp,i+1)



def removeTree(videoID:str):
    pass

def connect():
    global client
    client = MongoClient("mongodb://azoam:"+config.MongoPass+
    "@cluster0-shard-00-00-r9vk0.gcp.mongodb.net:27017,cluster0-shard-"+
    "00-01-r9vk0.gcp.mongodb.net:27017,cluster0-shard-00-02-r9vk0.gcp."+
    "mongodb.net:27017/test?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin&retryWrites=true")

connect()
