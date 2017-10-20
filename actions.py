import paho.mqtt.client as mqtt
import json
from pprint import pprint
import time
import config
with open('actions.json') as data_file:    
    actions = json.load(data_file)


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

def process(text):
    for action in actions:
        for command in action["commands"]:
            if text == command["command"]:
                print("======== COMMAND ==========")
                print("DEVICE: %s" % action['device'])
                print("MQTT:   %s" % action['mqtt'])
                print("VALUE:  %s" % command["value"])                
                print("ANSWER: %s" % command["answer"])              

                publish(action['mqtt']['topic'], command["value"], 0, False)
                return True

    return False


