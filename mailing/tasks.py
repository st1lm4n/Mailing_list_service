from time import timezone

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from .models import Mailing

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def update_mailing_statuses():
    """Периодическая задача для обновления статусов"""
    now = timezone.now()

    # Обновление статусов для активных рассылок
    for mailing in Mailing.objects.filter(
        status__in=[Mailing.STATUS_CREATED, Mailing.STATUS_STARTED]
    ):
        if now > mailing.end_time:
            mailing.status = Mailing.STATUS_COMPLETED
            mailing.save(update_fields=["status"])
        elif mailing.start_time <= now <= mailing.end_time:
            if mailing.status == Mailing.STATUS_CREATED:
                mailing.status = Mailing.STATUS_STARTED
                mailing.save(update_fields=["status"])


def schedule_mailing(mailing_id):
    """Планирование конкретной рассылки"""
    mailing = Mailing.objects.get(id=mailing_id)

    # Удаляем старую задачу если есть
    job_id = f"mailing_{mailing_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    # Планируем новую задачу
    scheduler.add_job(
        send_mailing_task,
        "date",
        run_date=mailing.start_time,
        args=[mailing_id],
        id=job_id,
    )


# Запуск планировщика при старте приложения
scheduler.start()
