from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        activation_link = f"http://localhost:8500/activate/{instance.pk}/"
        subject = "Activa tu cuenta"
        message = f"Hola {instance.username},\n\nPor favor activa tu cuenta haciendo clic en el siguiente enlace:\n{activation_link}"

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.email],
            fail_silently=False,
        )
