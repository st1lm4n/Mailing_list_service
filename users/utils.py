from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from config import settings


def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verify_url = request.build_absolute_uri(
        f'/verify-email/{uid}/{token}/'
    )
    send_mail(
        'Подтверждение email',
        f'Перейдите по ссылке: {verify_url}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False
    )