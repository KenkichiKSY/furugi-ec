from django import forms
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User
from .models import Address


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['recipient_name', 'postal_code', 'prefecture', 'city', 'building', 'phone_number', 'is_default']
