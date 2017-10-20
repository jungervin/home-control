import paho.mqtt.client as mqtt
import json
from pprint import pprint
import time
import config

from gtts import gTTS
#from subprocess import call
import subprocess

with open('actions.json') as data_file:    
    actions = json.load(data_file)


# https://github.com/merlinschumacher/ct-google-assistant-sdk/blob/master/assistant.py
def speak_tts(text, lang="en-us"):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("audio/answer.mp3")
    subprocess.Popen(["mpg123", "audio/answer.mp3"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
 
def ding():
    subprocess.Popen(["mpg123", "audio/ding.mp3"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #call(["mpg123", "audio/ding.mp3"])

def publish(topic, msg, qos=0, retain=False):
    try:
        print("======== PUBLISH ==========")
        print("PUBLISH TOPIC:  %s" % topic)
        print("PUBLISH MSG:    %s" % msg)
        print("PUBLISH QOS:    %s" % qos)
        print("PUBLISH RETAIN: %s" % retain)
        
        client = mqtt.Client()
        client.username_pw_set(config.mqtt_user,config.mqtt_pw)
        client.connect(config.mqtt_broker, config.mqtt_port, 1)
        client.publish(topic, msg, qos=qos, retain=retain)
        client.disconnect()
    except BaseException as e:
        print("Exception at publish")
        print(str(e))

def process(text, assistant):
    for action in actions:
        for command in action["commands"]:
            if text == command["command"]:
                assistant.stop_conversation()
                print("======== COMMAND ==========")
                print("DEVICE: %s" % action['device'])
                print("MQTT:   %s" % action['mqtt'])
                print("VALUE:  %s" % command["value"])                
                print("ANSWER: %s" % command["answer"])              

                publish(action['mqtt']['topic'], command["value"], 0, False)
                speak_tts(command["answer"])

                return True

    return False


