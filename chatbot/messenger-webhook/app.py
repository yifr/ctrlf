#Python libraries that we need to import for our bot
import re
import json
import random
import logging
import requests
import secret_info
from wit import Wit
from pymessenger.bot import Bot
from flask import Flask, request, Response,jsonify


app = Flask(__name__)
MESSENGER_TOKEN = secret_info.get_messenger_token()
WIT_TOKEN = secret_info.get_wit_token()
VERIFY_TOKEN = 'STARTED_FROM_NEW_BRUNSWICK_NOW_WE_HERE'
bot = Bot(MESSENGER_TOKEN)
#wit_bot = Wit(WIT_TOKEN)

user = {'playlist': None, 'topic':None, 'subtopic': None}

#We will receive messages that Facebook sends our bot at this endpoint 
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        data = request.get_data().decode('utf-8')
        data = json.loads(data)
        for entry in data['entry']:
            print('Entry ---->', entry)
            if 'message' in entry['messaging'][0]:
                    user_message = entry['messaging'][0]['message']['text']
                    user_id = entry['messaging'][0]['sender']['id']
                    response = {
                        'recipient' : {'id': user_id},
                        'message' : {}
                    }
                    text = handle_message(user_message, user_id)
                    bot.send_text_message(user_id, text)
                    response['message']['text'] = text
                    response['Content-type'] = 'application/json'
                    r = requests.post('https://graph.facebook.com/v2/6/me/messages/?access_token'+MESSENGER_TOKEN, json=response)
                    return jsonify({"status":200})
            else:
                return jsonify({'status':200})     
'''
        # get whatever message a user sent the bot
        data = request.json
        if data['object'] == 'page':
            #for entry in data['entry']:
            messages = data['entry'][0]['messaging']
            print('\n',  messages)
            if messages[0]:
                print()
                if len(messages[0]) <= 6:
                    message = messages[0]
                    print('message[message]:', message['message'])
                    fb_id = message['sender']['id']
                    text = message['message']['text']
                    #response = wit_bot.message(msg=text, context={'session_id':fb_id})
                    handle_message(response, fb_id)
                     
            else:
                fb_id = message['sender']['id']
                send_message(fb_id, 'Something has gone wrong')
                return "Failure"
        else:
            return 'Received Different Event'
    return "Success!" 


def get_entity_value(entities, entity):
    if entity not in entities:
        return None
    val = entities[entity][0]
    if not val:
        return None

    return val['value'] if isinstance(val, dict) else val
'''

def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error 
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


def send_message(sender_id, text):
    data = {
        'recipient': {'id': sender_id},
        'message': {'text': text}
    }
    query_string = 'access_token=' + MESSENGER_TOKEN
    response = requests.post('https://graph.facebook.com/me/messages?'+query_string,json=data)

    return response.content

def end_sequence(message):
    message = message.lower()
    print("END_SEQUENCE: ", message)
    if message == 'no' or message == 'nope' or message == 'na' or message == "that's it" or message == "i'm done" or message == "nothing else" or message == "that's all":
        return True
    else:
        return False

def integrate_cool_stuff(topic, subtopic):
    print('TOPIC, SUBTOPIC', topic, subtopic)
    url = 'http://ec2-34-201-73-49.compute-1.amazonaws.com:6969/searchSubtopic'
    data = {'topic':topic, 'subtopic':subtopic}
    r = requests.post(url, json=data)
    response = r.json()
    return response


#Create time embedded youtube links
def get_timestamped_links(response):
    base_url = response['videoLink']
    time_tags = response['timeTags']
    ret_string = ""
    i = 1
    for tag in time_tags:
        times = tag.split('.')
        total_time = times[0] * 60 + times[1]
        timetagged = base_url + '&t='+str(total_time)
        ret_string += str(i) + ') ' + timetagged + '\n'
        i += 1

    return ret_string

def handle_message(response, fb_id):

    if user['playlist'] == None:
        if True:
            user['playlist'] = response
            return "Thanks! What's this video about?"
        else:
            return "Sorry, you need to give me a link to a video before I can help you"

    elif user['topic'] == None:
        user['topic'] = response
        return "Great! What subtopic do you want me to look for?"

    else:
        if end_sequence(response):
            user['playlist'] = None
            user['topic'] = None
            user['subtopic'] = None
            return "It\'s been a pleasure working with you!"
            

        else:
            subtopic = response.split(',')
            if len(subtopic) > 1:
                return "Whoa there! I am but a simple bot. What subtopic would you like to search first?" 

            else:
                response = integrate_cool_stuff(user['topic'], subtopic[0])
                ret_string = get_timestamped_links(response)
                return ret_string

    return "Sorry - something seems to have gone dreadfully wrong. Run while you still can."
    
    '''
    entities = response['entities']
    url = get_entity_value(entities, 'url')
    topic = get_entity_value(entities, 'topic')
    confirmation = get_entity_value(entities, 'confirmation')
    negative = get_entity_value(entities, 'negative')

    #Find URL
    if user['playlist'] is None:
        if url:   
            user['playlist'] = url

            if len(entities) == 1:
                response = "Thanks! Two more steps: \n1) Type the topic you're trying to learn about. \n2) The subtopics you are looking for in specific."
                send_message(fb_id, response) 
                return "Message sent"
            else:
               response = "Sorry, I only caught the url - could you tell me what the subject of the playlist is?"
               send_message(fb_id, response)
               return "Message sent"

    #Add user's topic:
    elif user['topic'] is None:
        if topic:
            if len(topic) == 1:
                user['topic'] = topic
                response = "Great! Now can you let me know the subtopics you want me to find?"
                send_message(fb_id, response)
                return "Message sent"
            
            if len(topic) > 1:
                user['topic'] = topic[0]
                response = topic[0] + " is pretty cool - I can only take care of one topic at a time, so let's start with that. \nWhat are some subtopics you want me to find the times for?"
                send_message(fb_id, response)
                return "Message sent"

    #Add user's subtopics
    else:
        if topic == None:
            if confirmation:
                response = "Thanks for confirming that. I'll add " + response['text'] + " to the list of subtopics to flag for you. Anything else?"
                user['topic'].append(response['text'])
                send_message(fb_id, response)
                return "Message sent"
            else:
                    response = "I'm still pretty new to this, so I'm not sure I got what you said. Just to confirm, you're looking for " + response['text'] + '?'
                    send_message(fb_id, response)
                    return "Message sent"

        else:
            if negative:
                response = "Awesome. I'll look through these videos for anything interesting and get back to you in a minute"
                #CALL SAM AND SRI'S SEARCH CLIENT
                send_message(fb_id, response)
                return "Message sent"

            else:
                for thing in topic:
                    user['subtopics'].append(thing)
                response = "I'll add what you just said to a subtopic list. Anything else?"
                send_message(fb_id, response)
                return "Message sent"
    return send_message(fb_id, 'Sorry, something went wrong. Enter a link and try again') 
    '''

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
