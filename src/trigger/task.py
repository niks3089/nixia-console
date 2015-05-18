import paramiko 
import time
import redis
import ujson 
import os
import subprocess
from django_rq import job
from django.conf import settings
from adjacent import Client

"""
1. We need redis server to be running.
2. We need rqworker to be running in the background.
3. We need centrifuge to be running in the background.
"""
""" 
This is called by run-worker.py when spawn_nixia times out.
We need to let the user know that we failed to create nixia.
"""
def handle_failed_nixia(job, exc_type, exc_value, traceback):
    args = job.args

    # Before deleting, publish that it failed to the client
    # publish using centrifuge.
    client = Client()
    error_json = {}
    error_json['error'] = exc_value
    client.publish(args[0], ujson.dumps(error_json))
    response = client.send()

    # Clear the failed queue
"""
    q = django_rq.get_failed_queue()
    while True:
        job = q.dequeue()
        if not job:
            break
        job.delete()  # Will delete key from Redis
"""

@job
def spawn_nixia(data_channel, final_config,nixia_cred):
    """ 
    input should be validated form. 
    subscribe to the channel which nixia should connect to
    Convert the form to xml.
    1. If nixia should be done locally,
        Write the xml to /tmp directory.
        Fork nixia

    2. If nixia is done remotely,
        ssh into the machine and trigger nixia    

    """
    local_file = "/tmp/configlocal_%s" % data_channel
    remote_file = "/tmp/configremote_%s" % data_channel
    with open(local_file, "w") as outfile:
        ujson.dump(final_config, outfile) 

    if nixia_cred['location'] == 'local':
        dev_null = open(os.devnull, 'w')
        subprocess.Popen(["nixia", "-g", "-f", local_file], stdout=dev_null,
                stderr=subprocess.STDOUT)
    else:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(nixia_cred['ip'], username=nixia_cred['username'], password=nixia_cred['password'])
        sftp = ssh.open_sftp()
        sftp.put(local_file, remote_file)
        sftp.close()
        stdin, stdout, stderr = ssh.exec_command('nohup nixia -g -f '
        '%s > /dev/null 2>&1 &' % remote_file)

    pubsub = redis.Redis(settings.CONFIGURED_IP).pubsub()
    pubsub.subscribe([data_channel])

    for item in pubsub.listen():
        if item['data'] == "ALIVE":
            print "We got alive command"
            # We got connected.
            break
    return True 

#Task started just once.
@job
def subscriber():
    r = redis.Redis(settings.CONFIGURED_IP)
    pubsub = r.pubsub()
    pubsub.subscribe(['default'])

    for item in pubsub.listen():
        if item['channel'] == "default":
            # We have got a subscriber
            pubsub.subscribe(item['data'])
        elif item['data'] == "ALIVE":
            # Keepalive coming from nixia backend. do nothing
            pass
        else:
            # Send it to centrifuge
            client = Client()
            client.publish(item['channel'], item['data'])
            response = client.send()

