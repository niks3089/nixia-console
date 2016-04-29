# -*- coding: utf-8 -*-
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.bootstrap import StrictButton, TabHolder, Tab
from django.http import HttpResponse
from django.http import HttpResponseRedirect

class HttpForm(forms.Form):

    url = forms.GenericIPAddressField(
        label = "HTTP Server IP",
        required = True,
    )

    http_version = forms.ChoiceField(
        label = "HTTP VERSION ",
        choices = (
            ('one.zero', "1.0"),  
            ('one.one', "1.1")
        ),
        widget = forms.RadioSelect,
        initial = 'one.one',
        required=False,
    )

    total_connections = forms.IntegerField(
        label = "Total Connections",
        initial = '1',
        required=False,
    )

    concurrency_connection = forms.IntegerField(
        label = "Concurrency",
        required=False,
    )

    connections_per_second = forms.IntegerField(
        label = "Connection per Second",
        required=False,
    )

    total_requests = forms.IntegerField(
        label = "Total Requests",
        required=False,
    )
    requests_per_second = forms.IntegerField(
        label = "Requests per Second",
        required=False,
    )
    divide_requests = forms.ChoiceField(
        label = "DIVIDE REQUESTS EQUALLY",
        choices = (
            ('true', "TRUE"),  
            ('false', "FALSE")
        ),
        widget = forms.RadioSelect,
        initial = 'false',
        required=False,
    )

    # Bootstrap 

    helper = FormHelper()
    helper.field_template = 'bootstrap3/layout/inline_field.html'
    helper.form_class = 'form-vertical'
    helper.form_action = "."
    helper.layout = Layout( 
        TabHolder(
            Tab('General configuration',
                Field('http_version', style="background:;",css_class='input-xlarge'),
                Field('url', style="background:;",css_class='input-xlarge'),
            ),
            Tab('Connection configuration',
                Field('total_connections', style="background: ;",css_class='input-xlarge'),
                Field('concurrency_connection',style="background: ;", css_class='input-xlarge'),
                Field('connections_per_second', style="background: ;",css_class='input-xlarge'),
            ),
            Tab('Request configuration',
                Field('total_requests', style="background: ;",css_class='input-xlarge'),
                Field('requests_per_second',style="background: ;", css_class='input-xlarge'),
                Field('divide_requests', style="background: ;",css_class='input-xlarge'),
            ),
        ),

        FormActions(
            Submit('save_changes', 'RUN TEST', css_class="btn-primary"),
            #Submit('cancel', 'GO BACK', css_class="btn-danger" , onclick= "alert('Near');",
         HTML('<a class="btn btn-danger" href="../config">Go Back</a>'),        
        )
    )
