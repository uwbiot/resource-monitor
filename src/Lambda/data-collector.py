import greengrasssdk
import platform
import os
import json
import subprocess
import shlex

from datetime import datetime

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

# ------------------------------------------------------------------------------
def get_memory_info():
    """"""
    fd = open('/proc/meminfo').readlines()
    memory_info = dict((i.split()[0].rstrip(':'), int(i.split()[1])) for i in fd)

    total_mem = memory_info['MemTotal']
    free_mem = memory_info['MemFree']
    avail_mem = memory_info['MemAvailable']

    # publish information to the cloud
    #client.publish(
    #    topic='RM/Greengrass/data/MemTotal',
    #    payload=json.dumps({'MemTotal': total_mem})
    #)
    #client.publish(
    #    topic='RM/Greengrass/data/MemFree',
    #    payload=json.dumps({'MemFree': free_mem})
    #)
    #client.publish(
    #    topic='RM/Greengrass/data/MemAvailable',
    #    payload=json.dumps({'MemAvailable': avail_mem})
    #)
    return memory_info

# ------------------------------------------------------------------------------
def get_cpu_info():
    """"""
    fd = open('/proc/cpuinfo').readlines()
    #print fd
    fd = [_.replace("\n", "").replace("\t","") for _ in fd ]
    cpu_info = {}
    info_list = {}
    processor = ""
    for item in fd:
        data = item.split(":")
        desc = data[0]
        
        if len(data) == 2:
            info = data[1].lstrip()
        else:
            info = data[0], ""
        
        if desc == "processor":
            processor = info
        else:
            info_list[desc] = info
            
        if desc == "power management":
            cpu_info["processor " + processor] = info_list
            
    print "cpu_info"
    print cpu_info
    return cpu_info



# ------------------------------------------------------------------------------
def get_hostname():
    fd = subprocess.Popen(shlex.split('hostname'), stdout=subprocess.PIPE, shell=True)
    hostname, _ = fd.communicate()
    print(hostname)
    client.publish( # publish information to the cloud
        topic='RM/Greengrass/data/deviceId',
        payload=json.dumps({'deviceId': hostname})
    )
    return hostname

# ------------------------------------------------------------------------------
def get_disk_info():
    df = subprocess.Popen(shlex.split('df -h'), stdout=subprocess.PIPE, shell=True)
    dfdata, _ = df.communicate()
    dfdata = dfdata.replace("Mounted on", "Mounted_on")
    print "disk_info "
    print dfdata
    return dfdata

# ------------------------------------------------------------------------------
def get_cpu_temp():
    cpu_temp = subprocess.Popen(shlex.split('vcgencmd measure_temp'), stdout=subprocess.PIPE, shell=True)
    cpu_temp, _ = cpu_temp.communicate()
    print "cpu_temp " 
    print cpu_temp
    client.publish(
        topic='RM/Greengrass/data/Cpu_Temp',
        payload=json.dumps({'cpu_temp': cpu_temp})
    )
    return cpu_temp#.split('=')[1]


# ------------------------------------------------------------------------------
def get_lambdas():
    lambdas = subprocess.Popen(shlex.split('ls /greengrass/ggc/deployment/lambda'), stdout=subprocess.PIPE, shell=True)
    lambdas, _ = lambdas.communicate()
    print "lamdas"
    print lambdas
    client.publish(
        topic='RM/Greengrass/data/Lambdas',
        payload=json.dumps({'Lambdas': lambdas})
    )
    return lambdas

# ------------------------------------------------------------------------------
def run():
    date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    hostname = get_hostname()
    
    memory_info = get_memory_info()
    cpu_info = get_cpu_info()
    
    cpu_temp = get_cpu_temp()
    disk_info = get_disk_info()
    lambdas = get_lambdas()
    
    if not my_platform:
        client.publish(
            topic='RM/Greengrass/data',
            payload=json.dumps({
                'deviceId': 'Greengrass', #ip,
                'timestamp': date_time
            })
        )
    else: #greengrass platform
        client.publish(
            topic='RM/Greengrass/data',
            payload=json.dumps({
                'deviceId': hostname,
                'timestamp': date_time,
                'platform': my_platform,
                'cpu_info': cpu_info,
                'mem_info': memory_info,
                'disk_info': disk_info,
                'cpu_temp': cpu_temp,
                'lambdas_deployed': lambdas
            })
        )

# ------------------------------------------------------------------------------
def lambda_handler(event, context):
    run()
