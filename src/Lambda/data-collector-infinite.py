import greengrasssdk
import platform
import os
import json
import subprocess

from datetime import datetime

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

def get_ip():
    ip = subprocess.check_output(['hostname', '-I']).split()[0]
    client.publish( # publish information to the cloud
        topic='RM/Greengrass/data/deviceId',
        payload=json.dumps({'deviceId': ip})
    )
    return ip

def get_disk_info():
    df = os.popen("df -h /")
    i = 0
    while i<3:
        i = i + 1
        line = df.readline()
        if i==1:
            desc = line.split()[0:6]
        if i==2:
            info = line.split()[0:6]

    # publish information to the cloud
    for i in range(1,4):
        client.publish(
            topic='RM/Greengrass/data/Disk_{}'.format(desc[i]),
            payload=json.dumps({'Disk_{}'.format(desc[i]): info[i]})
        )
    return { desc[1]: info[1], desc[2]: info[2], desc[3]: info[3], desc[4]: info[4]}

def get_memory_info():
    memory_info = dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/meminfo').readlines())

    total_mem = memory_info['MemTotal']
    free_mem = memory_info['MemFree']
    avail_mem = memory_info['MemAvailable']

    # publish information to the cloud
    client.publish(
        topic='RM/Greengrass/data/MemTotal',
        payload=json.dumps({'MemTotal': total_mem})
    )
    client.publish(
        topic='RM/Greengrass/data/MemFree',
        payload=json.dumps({'MemFree': free_mem})
    )
    client.publish(
        topic='RM/Greengrass/data/MemAvailable',
        payload=json.dumps({'MemAvailable': avail_mem})
    )
    return memory_info

def get_cpu_temp():
    cpu_temp = subprocess.check_output(['vcgencmd', 'measure_temp']).split('=')[1]
    client.publish(
        topic='RM/Greengrass/data/Cpu_Temp',
        payload=json.dumps({'cpu_temp': cpu_temp})
    )
    return cpu_temp

def get_lambdas():
    lambdas = subprocess.check_output(['ls', '/greengrass/ggc/deployment/lambda'])
    client.publish(
        topic='RM/Greengrass/data/Lambdas',
        payload=json.dumps({'Lambdas': lambdas})
    )
    return lambdas

def run():
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #ip = get_ip()
    #memory_info = get_memory_info()
    #cpu_temp = get_cpu_temp()
    #disk_info = get_disk_info()
    #lambdas = get_lambdas()

    #print ip
    #print memory_info
    #print cpu_temp
    #print disk_info
    #print lambdas

    if not my_platform:
        client.publish(
            topic='RM/Greengrass/data',
            payload=json.dumps({
                'deviceId': 'Greengrass-Infinite', #ip,
                'timestamp': date_time
            })
        )

    else: #greengrass platform
        client.publish(
            topic='RM/Greengrass/data',
            payload=json.dumps({
                'deviceId': 'Greengrass-Infinite', #ip,
                'timestamp': date_time,
                'platform': my_platform
                #'cpu_temp': cpu_temp,
                #'disk_info': disk_info,
                #'lambdas_deployed': lambdas
            })
        )

# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def lambda_handler(event, context):
    run()


#cd /greengrass/ggc/core/
#sudo ./greengrassd start
