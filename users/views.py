from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from config import settings
from mailing.views import UserRegisterForm
from .models import User


@permission_required("auth.can_disable_user")
def toggle_user_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    return redirect("user_list")


@staff_member_required
def toggle_user_block(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()
    return redirect("user_list")


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Аккаунт не активен до подтверждения
            user.save()

            # Отправка письма с подтверждением
            current_site = get_current_site(request)
            mail_subject = "Активация вашего аккаунта"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_url = reverse("activate", args=[uid, token])
            activation_link = f"http://{current_site.domain}{activation_url}"

            message = render_to_string(
                "users/activation_email.html",
                {
                    "user": user,
                    "activation_link": activation_link,
                },
            )

            send_mail(
                mail_subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return redirect("activation_sent")
    else:
        form = UserRegisterForm()
    return render(request, "users/register.html", {"form": form})


def activation_sent(request):
    return render(request, "users/activation_sent.html")


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
