from django import forms
from django.contrib.auth.models import User
import re




class ContactForm(forms.Form):
  name    = forms.CharField(max_length=200, required=True, error_messages={'required':"Please enter your name"})
  email   = forms.EmailField(max_length=200, required=True, error_messages={'required':"Please enter your email address"})
  message = forms.CharField(required=True, widget=forms.Textarea(attrs={'rows': 5,'cols': 10}), error_messages={'required':"Please enter your message"})


  def clean_name(self):
    name = self.cleaned_data.get('name')
    if not re.match(r'^[A-Za-z\s]+$',name):
      raise forms.ValidationError("Name can only contain Characters")
    return name
  