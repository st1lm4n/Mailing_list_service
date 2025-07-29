import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import MailingAttempt

logger = logging.getLogger(__name__)


def send_mailing(mailing):
    """Отправка рассылки всем получателям"""
    try:
        # логика отправки
        logger.info(f"Рассылка {mailing.id} отправлена")
    except Exception as e:
        logger.error(f"Ошибка отправки: {str(e)}")

    recipients = mailing.get_active_recipients()
    sent_count = 0

    for recipient in recipients:
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=False
            )
            status = MailingAttempt.STATUS_SUCCESS
            response = 'OK'
            sent_count += 1
        except Exception as e:
            status = MailingAttempt.STATUS_FAIL
            response = str(e)

        # Создаем запись о попытке
        MailingAttempt.create_attempt(
            mailing=mailing,
            recipient=recipient,
            status=status,
            response=response
        )

    # Обновляем статус рассылки если это первая отправка
    if sent_count > 0 and mailing.status == mailing.STATUS_CREATED:
        mailing.status = mailing.STATUS_STARTED
        mailing.save(update_fields=['status'])

    return sent_count
