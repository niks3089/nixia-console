# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.bootstrap import StrictButton, TabHolder, Tab
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login

class ConfigForm(forms.Form):

    install = forms.ChoiceField(
        label = "Pick your choice:",
        choices = (
            ('install_antik', "Install ANTIK"),  
            ('run_antik', "Run Client")
        ),
        widget = forms.RadioSelect,
        initial = 'run_antik',
        required = True,
    )
    protocols = forms.MultipleChoiceField(
        choices = (
            ('http', 'Hyper Text Transfer Protocol - HTTP'), 
        ),
        label = "Select the protocols to run",
        initial = 'http', 
        widget = forms.CheckboxSelectMultiple,
        required= True,
    )
    location = forms.ChoiceField(
        choices = (
            ('local' , 'Run client on local machine'),
            ('remote' , 'Run client on remote machine'),
        ),
        label = "Where do you want to run the Client?",
        widget = forms.RadioSelect,
        initial='local',
        required = False,
    )
    ip = forms.GenericIPAddressField(
        label = "Remote IP address",
        required = False,
    )
    username = forms.CharField(
        label="Enter username",
        required= False,
    )
    password = forms.CharField(
        label="Enter password",
        required = False,
        widget= forms.PasswordInput,
    )
    
    # Bootstrap 
    helper = FormHelper()
    helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.form_class = 'form-vertical'
    helper.form_action = "."
    helper.layout = Layout(
        Field('install'),
        Field('location'),
        Field('ip'),
        Field('username'),
        Field('password' ),
        Field('protocols'),
        FormActions(
            Submit('next', 'Next', css_class="btn-primary"),
            HTML('<a class="btn btn-danger" href="../">Go Back</a>'),        
            #Submit('cancel', 'Cancel', css_class="btn-danger"),
        ),
        
    )
