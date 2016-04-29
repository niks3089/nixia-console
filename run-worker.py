#!/usr/bin/env python
import sys
import redis
import os
from rq import Queue, Connection, Worker
from receiver import task 

CONFIGURED_IP = os.environ['CONF_IP']

with Connection(redis.Redis(CONFIGURED_IP)):
    q = Queue() #Create an RQ Queue
    w = Worker([q], exc_handler=task.handle_failed_antik)
    w.work()
