from django.contrib import admin
from .models import *

admin.site.register(Recipient)
admin.site.register(Message)
admin.site.register(Mailing)
admin.site.register(MailingAttempt)
