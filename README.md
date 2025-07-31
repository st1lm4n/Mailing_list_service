# 🚀 Сервис управления рассылками

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-brightgreen.svg)](https://djangoproject.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Профессиональный сервис для управления email-рассылками с аналитикой и автоматизацией. Позволяет создавать, планировать и отслеживать рассылки для ваших клиентов.

## ✨ Основные возможности

- **Управление клиентами**:
  - Добавление/редактирование получателей
  - Группировка клиентов
  - Добавление комментариев
  
- **Создание сообщений**:
  - Шаблоны писем
  - Визуальный редактор
  - История изменений

- **Работа с рассылками**:
  - Планирование отправки
  - Автоматический и ручной запуск
  - Статусы рассылок (Создана, Запущена, Завершена)
  
- **Аналитика и отчеты**:
  - Статистика по успешным/неудачным отправкам
  - Детальные логи попыток
  - Интеграция с почтовыми сервисами

- **Безопасность и доступ**:
  - Двухфакторная аутентификация
  - Ролевая модель (Пользователи/Менеджеры)
  - Восстановление пароля

## 🛠 Технологический стек

- **Backend**: 
  - Python 3.10+
  - Django 4.2
  - Django REST Framework
  - Celery + Redis
  - PostgreSQL

- **Frontend**:
  - Bootstrap 5.3
  - HTML5/CSS3
  - JavaScript (Vanilla)
  - Chart.js для графиков

- **Инфраструктура**:
  - Docker
  - Nginx
  - Gunicorn
  - Sentry для мониторинга ошибок

## ⚙️ Установка и запуск

### Требования:
- Python 3.10+
- PostgreSQL
- Redis
- SMTP сервер (или тестовый аккаунт Mailtrap)

### Шаги установки:

1. Клонировать репозиторий:
```bash
git clone https://github.com/st1lm4n/Mailing-list-service.git
cd Mailing-list-service
```

2. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Настройка окружения:
Создать файл ```.env``` в корне проекта (пример в ```.env.example```):
```ini
SECRET_KEY=ваш_секретный_ключ
DEBUG=True
DB_URL=postgres://user:password@localhost:5432/dbname
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=ваш@email.com
EMAIL_PASSWORD=пароль
REDIS_URL=redis://localhost:6379/0
```

5. Применить миграции:
```bash
python manage.py migrate
```

6. Создать суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустить сервер:
```bash
python manage.py runserver
```

8. Запустить Celery worker (в отдельном терминале):
```bash
celery -A mailing_service worker -l info -P gevent
```

9. Запустить Celery beat для периодических задач:
```bash
celery -A mailing_service beat -l info
```
Приложение будет доступно по адресу: http://localhost:8000

## 📋 Функциональные роли

|Роль|Возможности|
|-|-----------|
|Пользователь|Управление своими рассылками и клиентами, просмотр статистики|
|Менеджер|Просмотр всех рассылок, блокировка пользователей, управление активностью|
|Администратор|Полный доступ ко всем функциям системы|