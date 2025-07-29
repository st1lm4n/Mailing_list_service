from time import timezone

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from config import settings

User = get_user_model()


class Recipient(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    comment = models.TextField(blank=True)


class Message(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    subject = models.CharField(max_length=255)
    body = models.TextField()


class Mailing(models.Model):
    """Модель для управления рассылками"""

    # Варианты статусов
    STATUS_COMPLETED = "completed"
    STATUS_CREATED = "created"
    STATUS_STARTED = "started"
    STATUS_CHOICES = (
        (STATUS_CREATED, "Создана"),
        (STATUS_STARTED, "Запущена"),
        (STATUS_COMPLETED, "Завершена"),
    )

    # Основные поля
    start_time = models.DateTimeField(
        verbose_name="Время начала рассылки",
        help_text="Дата и время первой отправки рассылки",
    )
    end_time = models.DateTimeField(
        verbose_name="Время окончания рассылки",
        help_text="Дата и время окончания отправки рассылки",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус рассылки",
        db_index=True,
    )

    # Связи с другими моделями
    message = models.ForeignKey(
        "Message",
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Сообщение",
    )
    recipients = models.ManyToManyField(
        "Recipient", related_name="mailings", verbose_name="Получатели"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mailings",
        verbose_name="Владелец",
        null=True,  # Разрешаем null для админки
        blank=True,
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-start_time"]
        permissions = [
            ("can_disable_mailing", "Может отключать рассылку"),
        ]

    def __str__(self):
        return f"Рассылка #{self.id} ({self.get_status_display()})"

    def clean(self):
        """Валидация временных интервалов"""
        super().clean()

        # Проверка, что время начала раньше времени окончания
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                {"end_time": "Время окончания должно быть позже времени начала"}
            )

        # Проверка статуса при изменении
        if self.pk:
            original = Mailing.objects.get(pk=self.pk)
            if (
                original.status == self.STATUS_COMPLETED
                and self.status != self.STATUS_COMPLETED
            ):
                raise ValidationError(
                    {"status": "Завершенную рассылку нельзя изменить"}
                )

    def save(self, *args, **kwargs):
        """Автоматическое обновление статуса при сохранении"""
        now = timezone.now()

        # Автоматическое определение статуса
        if self.start_time <= now <= self.end_time:
            self.status = self.STATUS_STARTED
        elif now > self.end_time:
            self.status = self.STATUS_COMPLETED

        super().save(*args, **kwargs)

        # Если рассылка активна - планируем отправку
        if self.status == self.STATUS_STARTED:
            from .tasks import schedule_mailing_task

            schedule_mailing_task(self.id)

    def send_immediately(self):
        """Немедленная отправка рассылки"""
        from .services import send_mailing

        if self.status != self.STATUS_COMPLETED:
            return send_mailing(self)
        return False

    def get_active_recipients(self):
        """Получение активных получателей рассылки"""
        return self.recipients.filter(is_active=True)

    def update_status_based_on_time(self):
        """Обновление статуса на основе текущего времени"""
        now = timezone.now()
        if now > self.end_time:
            self.status = self.STATUS_COMPLETED
            self.save(update_fields=["status"])
        return self.status

    def save(self, *args, **kwargs):
        now = timezone.now()

        # Автоматическое обновление статуса
        if self.start_time <= now <= self.end_time:
            self.status = self.STATUS_STARTED
        elif now > self.end_time:
            self.status = self.STATUS_COMPLETED

        super().save(*args, **kwargs)

        # Планирование задачи при активации рассылки
        if self.status == self.STATUS_STARTED:
            from .tasks import schedule_mailing

            schedule_mailing(self.id)


class MailingAttempt(models.Model):
    """Модель для хранения попыток отправки рассылки"""

    # Варианты статусов
    STATUS_SUCCESS = "success"
    STATUS_FAIL = "fail"
    STATUS_CHOICES = (
        (STATUS_SUCCESS, "Успешно"),
        (STATUS_FAIL, "Не успешно"),
    )

    # Основные поля
    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Время попытки")
    status = models.CharField(
        max_length=7, choices=STATUS_CHOICES, verbose_name="Статус попытки"
    )
    server_response = models.TextField(
        blank=True, null=True, verbose_name="Ответ сервера"
    )

    # Связи с другими моделями
    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )
    recipient = models.ForeignKey(
        "Recipient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Получатель",
    )

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ["-attempt_time"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["attempt_time"]),
        ]

    def __str__(self):
        return (
            f"Попытка #{self.id} для "
            f"рассылки #{self.mailing_id} ({self.get_status_display()})"
        )

    @classmethod
    def create_attempt(cls, mailing, recipient, status, response=None):
        """Создание записи о попытке отправки"""
        return cls.objects.create(
            mailing=mailing,
            recipient=recipient,
            status=status,
            server_response=response[:500] if response else None,
        )

    @property
    def is_successful(self):
        return self.status == self.STATUS_SUCCESS

    @property
    def recipient_email(self):
        return self.recipient.email if self.recipient else "N/A"
