
import greengrasssdk
import platform
import os
import json

from datetime import datetime
from threading import Timer

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

def run():
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #message = 'Sent from Greengrass Core. \nTime: {}\nPlatform: {}'.format(date_time, platform)
    if not my_platform:
        client.publish(
            topic='gg/resource/test',
            payload=json.dumps({
                'deviceId': 'Greengrass',
                'timestamp': date_time
            })
        )
    else: #greengrass platform
        client.publish(
            topic='gg/resource/test',
            payload=json.dumps({
                'deviceId': 'Greengrass',
                'timestamp': date_time,
                'platform': my_platform
            })
        )

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def lambda_handler(event, context):
    return
