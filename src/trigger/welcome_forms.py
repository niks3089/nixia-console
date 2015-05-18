from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit, HTML, Button, Row, Field
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.bootstrap import StrictButton, TabHolder, Tab

class WelcomeForm(forms.Form):

	
	login = forms.MultipleChoiceField(
		label = "Welcome User : ",
		required = False,
        	choices = (
            		('option_one', "Enter as a Guest User"),  
        	),
		widget = forms.CheckboxSelectMultiple,
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
                
		Field('login' ),
		Field('username'),
		Field('password' ),
		FormActions(
			Submit('save_changes', 'GO', css_class="btn-primary"),
			HTML('<a class="btn btn-danger" href="../">Cancel</a>'),        
			#Submit('cancel', 'CANCEL', css_class="btn-danger"),
		)

	)


