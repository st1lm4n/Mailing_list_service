from django import forms
from django.core.exceptions import ValidationError

from .models import *

class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = '__all__'

    def clean(self):
        if self.cleaned_data['start_time'] > self.cleaned_data['end_time']:
            raise ValidationError("Время окончания должно быть позже времени начала")