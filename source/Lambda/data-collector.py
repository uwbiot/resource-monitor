import greengrasssdk
import platform
import os
import json
import subprocess
import shlex
from os import statvfs

from datetime import datetime

# Creating a greengrass core sdk client
client = greengrasssdk.client('iot-data')
# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()

# ------------------------------------------------------------------------------
def get_memory_info():
    """"""
    fd = open('/proc/meminfo').readlines()
    memory_info = dict((i.split()[0].rstrip(':'), str(i.split()[1])) for i in fd)

    total_mem = memory_info['MemTotal']
    free_mem = memory_info['MemFree']
    avail_mem = memory_info['MemAvailable']

    return memory_info

# ------------------------------------------------------------------------------
def get_cpu_info():
    """"""
    fd = open('/proc/cpuinfo').readlines()
    fd = [_.replace("\n", "").replace("\t","") for _ in fd ]
    
    cpu_info = {}
    info_list = {}
    processor = ""
    
    for item in fd:
        data = item.split(":")
        desc = data[0]
        
        if len(data) == 2:
            info = data[1].lstrip()

        if desc == "processor":
            processor = info
        else:
            info_list[desc] = info
            
        if desc == "power management":
            if '' in info_list:
                del info_list['']
                
            info_list[desc] = "n/a"
            cpu_info["processor " + processor] = info_list
            
    for c in cpu_info:
        if '' in cpu_info[c]:
            del cpu_info[c]['']

    return cpu_info

# ------------------------------------------------------------------------------
def get_hostname():
    try: 
        hostname = subprocess.check_output("hostname", stderr=subprocess.STDOUT, shell=True)
    except Exception as err:
        hostname = err.output
    
    hostname = "Greengrass"
    return hostname

# ------------------------------------------------------------------------------
def get_disk_info():

    with open("/proc/mounts", "r") as mounts:
        split_mounts = [s.split() for s in mounts.read().splitlines()]

    data = str()
    
    for p in split_mounts:
        stat = statvfs(p[1])
        block_size = stat.f_bsize
        blocks_total = stat.f_blocks
        blocks_free = stat.f_bavail

        size_mb = float(blocks_total * block_size) / 1024 / 1024
        free_mb = float(blocks_free * block_size) / 1024 / 1024

        data += "{0:24} {1:24} {2:16} {3:16} {4:10.2f}MiB {5:10.2f}MiB ".format(
                p[0], p[1], blocks_total, blocks_free, size_mb, free_mb)

    data = [ _ for _ in data.split(" ") if _ is not '']

    disk_data = []
    desc = ["FS", "Mountpoint", "Blocks", "Blocks_Free", "Size", "Free"]
    info = {}
        
    #for item in 
    for i, item in enumerate( data ):
        if i % 6 == 0:
            disk_data.append(info)
        else:
            info[ desc[ i % 6 ] ] = item

    return disk_data

# ------------------------------------------------------------------------------
def get_cpu_temp():
    #cpu_temp = subprocess.Popen(shlex.split('vcgencmd measure_temp'), stdout=subprocess.PIPE, shell=True)
    #cpu_temp, _ = cpu_temp.communicate()
    try:
        cpu_temp = subprocess.check_output("vcgencmd measure_temp", stderr=subprocess.STDOUT, shell=True)
    except Exception as err:
        cpu_temp = err.output

    return cpu_temp


# ------------------------------------------------------------------------------
def get_lambdas():
    lambdas = "/greengrass/ggc/deployment/lambda does not exist"
    try:
        lambdas = os.listdir("/greengrass/ggc/deployment/lambda")
        lambdas = [ _ for _ in lambdas if not _.startswith('.')]
    except Exception as err:
        print err
   
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
            topic="RM/{}/data".format(hostname),
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
