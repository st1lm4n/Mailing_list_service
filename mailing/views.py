from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.cache import cache_page
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)

from .forms import *


class OwnerRequiredMixin:
    def test_func(self):
        return self.get_object().owner == self.request.user


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Managers").exists()


# Для клиентов
class RecipientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Recipient


class RecipientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("recipient_list")


class RecipientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("recipient_list")


class RecipientUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("recipient_list")


class RecipientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Recipient
    form_class = RecipientForm
    success_url = reverse_lazy("recipient_list")


# Для сообщений
class MassageListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Message


class MessageCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("message_list")


class MessageDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("message_list")


class MessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("message_list")


class MessageDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("message_list")


# Для рассылок
class MailingListView(ManagerRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing/mailing_list.html"

    def get_queryset(self):
        return Mailing.objects.select_related("message").prefetch_related("recipients")


class MailingCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing_list")


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing_list")


class MailingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing_list")


class MailingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailing_list")


# Главная страница
@cache_page(settings.CACHE_TTL)  # Кеш на 15 минут
def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(status="started").count()
    unique_recipients = Recipient.objects.distinct().count()

    return render(
        request,
        "home.html",
        {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "unique_recipients": unique_recipients,
        },
    )


@staff_member_required
def disable_mailing(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.status = "completed"
    mailing.save()
    return redirect("mailing_list")


@cache_page(settings.CACHE_TTL)
def user_statistics(request):
    mailings = Mailing.objects.filter(owner=request.user)
    stats = {
        "total": mailings.count(),
        "success": MailingAttempt.objects.filter(
            mailing__in=mailings, status="success"
        ).count(),
        "failed": MailingAttempt.objects.filter(
            mailing__in=mailings, status="failed"
        ).count(),
    }
    return render(request, "statistics.html", {"stats": stats})


# Статистика рассылок
@cache_page(settings.CACHE_TTL)
def mailing_stats(request):
    mailings = Mailing.objects.filter(owner=request.user)
    attempts = MailingAttempt.objects.filter(mailing__in=mailings)

    stats = {
        "total": attempts.count(),
        "success": attempts.filter(status="success").count(),
        "failed": attempts.filter(status="failed").count(),
    }
    return render(request, "mailing/stats.html", {"stats": stats})


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Пользователь неактивен до подтверждения
            user.save()

            # Отправка письма с подтверждением
            current_site = get_current_site(request)
            mail_subject = "Активация вашего аккаунта"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_url = reverse("activate", kwargs={"uidb64": uid, "token": token})
            activation_link = f"http://{current_site.domain}{activation_url}"

            send_mail(
                mail_subject,
                f"Пожалуйста, активируйте ваш аккаунт: {activation_link}",
                "noreply@yourservice.com",
                [user.email],
                fail_silently=False,
            )
            return redirect("activation_sent")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("home")
    else:
        return render(request, "users/activation_invalid.html")


def detailed_stats(request, mailing_id):
    mailing = get_object_or_404(Mailing, id=mailing_id)

    # Проверка прав доступа
    if not request.user.is_manager and mailing.owner != request.user:
        return HttpResponseForbidden()

    attempts = mailing.attempts.select_related("recipient")

    stats = {
        "total": attempts.count(),
        "success": attempts.filter(status="success").count(),
        "failed": attempts.filter(status="fail").count(),
        "unique_recipients": mailing.recipients.distinct().count(),
    }

    return render(
        request,
        "mailing/detailed_stats.html",
        {"mailing": mailing, "attempts": attempts, "stats": stats},
    )
