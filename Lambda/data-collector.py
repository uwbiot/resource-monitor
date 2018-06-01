import greengrasssdk
import platform
import os
import subprocess
import json

from datetime import datetime

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

def get_ip():
    return subprocess.check_output(['hostname', '-I'])

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
    return { desc[1]: info[1], desc[2]: info[2], desc[3]: info[3], desc[4]: info[4]}
    #return {'disk_size': info[1], 'disk_used': info[2], 'disk_avail': info[3], 'disk_use%': info[4]}

def get_memory_info():
    return dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/meminfo').readlines())

def get_cpu_info():
    return dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in open('/proc/cpuinfo').readlines())

def get_cpu_temp():
    return subprocess.check_output(['vcgencmd', 'measure_temp']).split('=')[1]

def get_lambdas():
    return subprocess.check_output(['ls', '/greengrass/ggc/deployment/lambda'])

def run():
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    memory_info = get_memory_info()
    #cpu_info = get_cpu_info()
    cpu_temp = get_cpu_temp()
    disk_info = get_disk_info()

    total_mem = memory_info['MemTotal']
    free_mem = memory_info['MemFree']
    avail_mem = memory_info['MemAvailable']

    lambdas = get_lambdas()

    print memory_info
    #print cpu_info
    print cpu_temp
    print disk_info
    print lambdas

    if not my_platform:
        client.publish(
            topic='resource/{}'.format(platform),
            payload=json.dumps({
                'deviceId': 'n/a',
                'timestamp': date_time
            })
        )
    else: #greengrass platform
        client.publish(
            topic='resource/{}'.format(get_ip()),
            payload=json.dumps({
                'deviceId': 'Greengrass',
                'timestamp': date_time,
                'platform': my_platform,
                'total_memory (kB)': total_mem,
                'free_memory (kB)' : free_mem,
                'avail_memory (kB)': avail_mem,
                'cpu_temp': cpu_temp,
                'disk_info': disk_info,
                'lambdas_deployed': lambdas
            })
        )
#run()
def lambda_handler(event, context):
    run()
