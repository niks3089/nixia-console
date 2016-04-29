import paramiko 
import time
import redis
import ujson 
import os
import subprocess
import django_rq
from django_rq import job
from django.conf import settings
from adjacent import Client
from datetime import timedelta 

channel_to_job_dict = {}

"""
Send json data to client/browser using centrifuge/adacent
"""
def send_data_to_client(channel, message, message_key=None):
    client = Client()
    if message_key is None:
        client.publish(channel, message)
    else:
        data = {}
        data[message_key] = message 
        client.publish(channel, ujson.dumps(data))
    return client.send()

"""
1. We need redis server to be running.
2. We need rqworker to be running in the background.
3. We need centrifuge to be running in the background.
"""
""" 
This is called by run-worker.py when spawn_antik times out.
We need to let the user know that we failed to create antik.
"""
def handle_failed_antik(job, exc_type, exc_value, traceback):
    args = job.args

    # Before deleting, publish that it failed to the client
    # publish using centrifuge.
    send_data_to_client(args[0], exc_value, 'error')

    # Clear the failed queue
"""
    q = django_rq.get_failed_queue()
    while True:
        job = q.dequeue()
        if not job:
            break
        job.delete()  # Will delete key from Redis
"""

"""
Invoked by the scheduler. This is an idication that
backend antik has crashed/unresponsive.
Inform to the client 
"""
def handle_unresponsive_antik(data_channel):
    del channel_to_job_dict[data_channel]
    send_data_to_client(data_channel, {'error' : 'antik is not responding'},
            'error')

@job
def spawn_antik(data_channel, final_config,antik_cred):
    """ 
    input should be validated form. 
    subscribe to the channel which antik should connect to
    Convert the form to xml.
    1. If antik should be done locally,
        Write the xml to /tmp directory.
        Fork antik

    2. If antik is done remotely,
        ssh into the machine and trigger antik    

    """
    local_file = "/tmp/configlocal_%s" % data_channel
    remote_file = "/tmp/configremote_%s" % data_channel
    with open(local_file, "w") as outfile:
        ujson.dump(final_config, outfile) 

    if antik_cred['location'] == 'local':
        dev_null = open(os.devnull, 'w')
        subprocess.Popen(["antik", "-g", "-f", local_file], stdout=dev_null,
                stderr=subprocess.STDOUT)
    else:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(antik_cred['ip'], username=antik_cred['username'], password=antik_cred['password'])
        sftp = ssh.open_sftp()
        sftp.put(local_file, remote_file)
        sftp.close()
        stdin, stdout, stderr = ssh.exec_command('nohup antik -g -f '
        '%s > /dev/null 2>&1 &' % remote_file)

    pubsub = redis.Redis(settings.CONFIGURED_IP).pubsub()
    pubsub.subscribe([data_channel])

    for item in pubsub.listen():
        if item['data'] == "KEEPALIVE":
            break

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
        elif item['data'] == "KEEPALIVE":
            # Keepalive coming from antik backend. 
            scheduler = django_rq.get_scheduler('default')
            job_second_list = channel_to_job_dict.get(item['channel'])
            if job_second_list is not None:
                job = job_second_list[0]
                second = job_second_list[1]
            else:
                job = None
                second = None
            if job is None:
                print "scehduled job. "
                job = scheduler.enqueue_in(timedelta(seconds = 5),
                        handle_unresponsive_antik, item['channel'])
                # Enqueue the job in a dict
                channel_to_job_dict[item['channel']] = [job, 1]
            elif job in scheduler:
                # Re-schedule
                if second + 1 == 5:
                    scheduler.cancel(job);
                    job = scheduler.enqueue_in(timedelta(seconds = 5),
                            handle_unresponsive_antik, item['channel'])
                    # Enqueue the job in a dict
                    channel_to_job_dict[item['channel']] = [job, 1]
                else:
                    second = second + 1
                    channel_to_job_dict[item['channel']] = [job, second]
        elif item['data'] == "DONE":
            if job in scheduler:
                scheduler.cancel(job);
                del channel_to_job_dict[item['channel']]
                send_data_to_client(item['channel'], {'notification' : 'test completed'},
                        'notification')
        else:
            # Received data. Send it Centrifuge 
            send_data_to_client(item['channel'], item['data'])
