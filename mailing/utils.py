from django.core.mail import send_mail
from django.urls import reverse

from .models import MailingAttempt
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def send_mailing(mailing):
    recipients = mailing.recipients.values_list('email', flat=True)

    for email in recipients:
        try:
            send_mail(
                mailing.message.subject,
                mailing.message.body,
                'noreply@yourdomain.com',
                [email],
                fail_silently=False
            )
            status = 'success'
            response = 'OK'
        except Exception as e:
            status = 'fail'
            response = str(e)

        MailingAttempt.objects.create(
            mailing=mailing,
            status=status,
            server_response=response
        )
