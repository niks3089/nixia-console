import django_rq
import redis
import task
import ujson 
import string
import random
from django.conf import settings
from django.http import HttpResponse
from welcome_forms import WelcomeForm
from http_forms import HttpForm
from config_forms import ConfigForm
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.core.context_processors import csrf

def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return HttpResponseRedirect('../')

def welcome_view(request):
    invalid_user = False
    welcome_form = WelcomeForm(request.POST)
    if request.method == 'POST':
        if welcome_form.is_valid():
            cleaned_data = welcome_form.clean()
            if 'login' in request.POST.keys():
                request.session['user_name'] = "Anonymous User" 
                return HttpResponseRedirect('../config')

            else:
                username = request.POST['username']
                request.session['user_name'] = username 
                password = request.POST['password']
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        # Redirect to a success page.
                        return HttpResponseRedirect('../config')
                    else:
                        # Return a 'disabled account' error message
                        return render(request, 'receiver/error1.html')
                else:
                    # Return an 'invalid login' error message.
                    invalid_user = True
    return render(request, 'receiver/welcome.html', {'welcome_form': welcome_form, 'invalid_user' : invalid_user})

# View to process form and render result
def result_view(request):
    # Get the next channel for this request.
    # Add the channel to the subscriber.
    # Enqueue the task of spawning antik
    # Return html
    #worker = django_rq.get_worker()
    #print "this is my worker" 
    r = redis.Redis(settings.CONFIGURED_IP)

    final_config = {}
    config_form = request.session.get('config_form')
    http_form = request.session.get('http_form')

    data_channel = config_form['redis_channel']
    
    # Create data for json 
    final_config['main'] = config_form
    final_config['http'] = http_form 
    r.publish("default", data_channel)
    
    #Extracting data to feed to antik 
    antik_cred = {}
    antik_cred['location'] = config_form['location']
    antik_cred['ip'] = config_form['ip']
    antik_cred['username'] = config_form['username']
    antik_cred['password'] = config_form['password']
    
    django_rq.enqueue(task.spawn_antik, 
        args = (data_channel, final_config, antik_cred), timeout=3)

    return_val = {}
    return_val['CENTRIFUGE_WEBSOCKET'] = settings.CENTRIFUGE_WEBSOCKET
    return_val['CENTRIFUGE_PROJECT_ID'] = settings.CENTRIFUGE_PROJECT_ID 

    return render(request, 'receiver/result.html', 
            {'data_channel' : data_channel,
             'CENTRIFUGE_WEBSOCKET' : settings.CENTRIFUGE_WEBSOCKET,
             'CENTRIFUGE_PROJECT_ID' : settings.CENTRIFUGE_PROJECT_ID, 
              'user' : request.session.get('user_name')})

def http_view(request):
    # Enqueue subscriber just once.
    # TODO: This code should ideally be in app config.
    if not hasattr(http_view, "subscriber_started"):
        django_rq.enqueue(task.subscriber, timeout=-1)
        http_view.subscriber_started = 1

    if request.method == 'POST':
        http_form = HttpForm(request.POST)
        if http_form.is_valid():
            request.session['http_form'] = extract_http_form(http_form)
            return HttpResponseRedirect('../result')
    else:
        http_form = HttpForm()

    return render(request, 'receiver/http.html', {'http_form': http_form,
        'user' : request.session.get('user_name')})

def config_view(request):
    if request.method == 'POST':
        config_form = ConfigForm(request.POST)
        if config_form.is_valid():
            request.session['config_form'] = extract_config_form(config_form)
            return HttpResponseRedirect('../http')
        else:
           print config_form.errors
    else:
        config_form = ConfigForm()

    return render(request, 'receiver/config.html', {'config_form': config_form,
        'user' : request.session.get('user_name')})

def extract_http_form(http_form):

    cleaned_data = http_form.clean()

    http = {}
    http['url'] = cleaned_data.get('url')
    http['http_version'] = cleaned_data.get('http_version')
    http['total_connections'] = cleaned_data.get('total_connections')
    http['concurrency_connection'] = cleaned_data.get('concurrency_connection')
    http['connections_per_second'] = cleaned_data.get('connections_per_second')
    http['total_requests'] = cleaned_data.get('total_requests')
    http['requests_per_second'] = cleaned_data.get('requests_per_second')
    http['divide_requests'] = cleaned_data.get('divide_requests')
    return http

def extract_config_form(config_form):
    
    cleaned_data = config_form.clean()

    config = {}
    config['name'] = 'test1'
    config['protocols'] = cleaned_data.get('protocols')
    config['ip'] = cleaned_data.get('ip')
    config['location'] = cleaned_data.get('location')
    config['username'] = cleaned_data.get('username')
    config['password'] = cleaned_data.get('password')
    config['redis_server'] = settings.CONFIGURED_IP
    config['redis_port'] = 6379
    config['redis_channel'] = ''.join(random.choice(
        string.ascii_uppercase + string.digits) for _ in range(100)) 
    print "random redis channel " + config['redis_channel']
    return config
