from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'address', 'gender', 'pincode', 'password1', 'password2']
    from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'name', 'phone', 'address', 'gender', 'pincode', 'password1', 'password2']

    # Optionally, you can add any custom validation for the fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Example of adding placeholders to the fields (optional)
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email'})
        self.fields['name'].widget.attrs.update({'placeholder': 'Enter your name'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Enter your phone number'})
        self.fields['address'].widget.attrs.update({'placeholder': 'Enter your address'})
        self.fields['gender'].widget.attrs.update({'placeholder': 'Select your gender'})
        self.fields['pincode'].widget.attrs.update({'placeholder': 'Enter your pincode'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Create a password'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm your password'})
