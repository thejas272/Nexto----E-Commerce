from django import forms
from django.contrib.auth.models import User
import re




class UserLoginForm(forms.Form):
  username = forms.CharField(max_length=100, required=True, error_messages={'required':"Please enter username"})
  password = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True, error_messages={'required':"Please enter password"})


    



class UserRegisterForm(forms.Form):
  first_name       = forms.CharField(max_length=100, required=True, error_messages={'required':"Please enter first name"})
  last_name        = forms.CharField(max_length=100, required=True, error_messages={'required':"Please enter last name"})
  email            = forms.EmailField(max_length=100, required=True, error_messages={'required':"Please enter email"})
  username         = forms.CharField(max_length=100, required=True, error_messages={'required':"Please enter username"})
  password         = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True, error_messages={'required':"Please enter password"})
  confirm_password = forms.CharField(max_length=100, widget=forms.PasswordInput, required=True, error_messages={'required':"Please confirm your password"})
  
  def clean_first_name(self):
    first_name = self.cleaned_data.get('first_name')
    if not re.match(r'^[A-Za-z\s]+$',first_name):
      raise forms.ValidationError('First name can only contain characters')
    return first_name
  
  def clean_last_name(self):
    last_name = self.cleaned_data.get('last_name')
    if not re.match(r'^[A-Za-z\s]+$',last_name):
      raise forms.ValidationError('Last name can only contain characters')
    return last_name
  
  def clean_email(self):
    email = self.cleaned_data.get('email')
    if User.objects.filter(email=email).exists():
      raise forms.ValidationError('Email already associated with an account')
    return email
  
  def clean_username(self):
    username = self.cleaned_data.get('username')
    if User.objects.filter(username=username).exists():
      raise forms.ValidationError('Username taken')
    return username

  def clean(self):
    cleaned_data = super().clean()
    password         = cleaned_data.get('password')
    confirm_password = cleaned_data.get('confirm_password') 

    if password != confirm_password:
      raise forms.ValidationError("Passwords do not match")
    return cleaned_data
  

class AddAddressForm(forms.Form):
  full_name       = forms.CharField(max_length=100, required=True, error_messages={'required':"Please enter a full name"})
  phone           = forms.CharField(max_length=10, required=True, error_messages={'required':"Please enter a phone"})
  house           = forms.CharField(max_length=100, required=True, error_messages={'required':"Please enter address line 1"})
  street          = forms.CharField(max_length=50, required=True, error_messages={'required':"Please enter a street name"})
  city            = forms.CharField(max_length=100, required=True, error_messages={'required':"Please enter a city"})
  state           =  forms.CharField(max_length=10, required=True, error_messages={'required':"Please enter a state"})
  landmark        = forms.CharField(max_length=300, required=True, error_messages={'required':"Please enter a landmark"})
  pincode         = forms.CharField(max_length=6, required=True, error_messages={'required':"Please enter a pincode"})
  default_address = forms.BooleanField(required=False)


  def clean_full_name(self):
    full_name = self.cleaned_data.get('full_name')
    if not re.match(r'^[A-Za-z\s]+$',full_name):
      raise forms.ValidationError("Name can only contain letters and whitespace")
    return full_name
  
  def clean_phone(self):
    phone = self.cleaned_data.get('phone')
    if not phone.isdigit():
      raise forms.ValidationError("Phone number can only contain digits")
    elif len(phone) != 10:
      raise forms.ValidationError("Phone number must have 10 digits")
    return phone
  
  def clean_pincode(self):
    pincode = self.cleaned_data.get('pincode')
    if not pincode.isdigit():
      raise forms.ValidationError("Cannot verify pincode entered")
    elif len(pincode) != 6:
      raise forms.ValidationError("Pincode must have 6 digits")
    return pincode

    

