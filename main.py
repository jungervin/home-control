#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# https://github.com/shivasiddharth/GassistPi
# https://github.com/merlinschumacher/ct-google-assistant-sdk
#

from __future__ import print_function
import argparse
import os.path
import os
import json

import google.auth.transport.requests
import google.oauth2.credentials
from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

import actions
import subprocess

def process_device_actions(event, device_id):
    if 'inputs' in event.args:
        for i in event.args['inputs']:
            if i['intent'] == 'action.devices.EXECUTE':
                for c in i['payload']['commands']:
                    for device in c['devices']:
                        if device['id'] == device_id:
                            if 'execution' in c:
                                for e in c['execution']:
                                    if e['params']:
                                        yield e['command'], e['params']
                                    else:
                                        yield e['command'], None


def process_event(event, device_id):
    print(event)
    print("\n")
    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        actions.ding()
        actions.publish('device/ghost/animate', 'ON1')
        
    if (event.type == EventType.ON_RESPONDING_STARTED and event.args and not event.args['is_error_response']):
        actions.publish('device/ghost/animate', 'ON2')

    if event.type == EventType.ON_RESPONDING_FINISHED:
        actions.publish('device/ghost/animate', 'OFF')

    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and event.args and not event.args['with_follow_on_turn']):
        actions.publish('device/ghost/animate', 'OFF')

def register_device(project_id, credentials, device_model_id, device_id):
    """Register the device if needed.
    Registers a new assistant device if an instance with the given id
    does not already exists for this model.
    Args:
       project_id(str): The project ID used to register device instance.
       credentials(google.oauth2.credentials.Credentials): The Google
                OAuth2 credentials of the user to associate the device
                instance with.
       device_model_id: The registered device model ID.
       device_id: The device ID of the new instance.
    """
    base_url = '/'.join([DEVICE_API_URL, 'projects', project_id, 'devices'])
    device_url = '/'.join([base_url, device_id])
    session = google.auth.transport.requests.AuthorizedSession(credentials)
    r = session.get(device_url)
    print(device_url, r.status_code)
    if r.status_code == 404:
        print('Registering....', end='', flush=True)    
        r = session.post(base_url, data=json.dumps({
            'id': device_id,
            'model_id': device_model_id,
            'client_type': 'SDK_LIBRARY'
        }))
        if r.status_code != 200:
            raise Exception('failed to register device: ' + r.text)
        print('\rDevice registered.')


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='Path to store and read OAuth2 credentials')
    parser.add_argument('--device_model_id', type=str,
                        metavar='DEVICE_MODEL_ID', required=True,
                        help='The device model ID registered with Google.')
    parser.add_argument('--project_id', type=str,
                        metavar='PROJECT_ID', required=False,
                        help='The project ID used to register device '
                        + 'instances.')
    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))
    with Assistant(credentials, args.device_model_id) as assistant:
        #subprocess.Popen(["aplay", "/home/pi/GassistPi/sample-audio-files/Startup.wav"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        events = assistant.start()
        print('device_model_id:', args.device_model_id + '\n' +
              'device_id:', assistant.device_id + '\n')
        if args.project_id:
            register_device(args.project_id, credentials,
                            args.device_model_id, assistant.device_id)
        for event in events:
            process_event(event, assistant.device_id)
            usrcmd=event.args
            
            if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
                if actions.process(event.args["text"].lower(), assistant):
                    assistant.stop_conversation()
                    pass

if __name__ == '__main__':
    main()

