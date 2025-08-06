from django.db.models.signals import post_save  # imports signal.
from django.dispatch import receiver  # receiver decorator.
from django.contrib.auth.models import User  # imports user.
from django.core.mail import send_mail  # imports send_mail.
from django.conf import settings  # imports settings.
from django.utils.http import urlsafe_base64_encode  # imports base64 encode.
from django.utils.encoding import force_bytes  # imports force_bytes.
from django.contrib.auth.tokens import default_token_generator  # imports token generator.
import django_rq  # imports django_rq for queuing.

@receiver(post_save, sender=User)  # receiver for post_save on user.
def send_activation_email(sender, instance, created, **kwargs):  # signal handler.
    if created and not instance.is_active:  # if new user and inactive.
        def send_email_task():  # defines task function.
            uid = urlsafe_base64_encode(force_bytes(instance.pk))  # encodes user id.
            token = default_token_generator.make_token(instance)  # generates token.
            activation_link = f"http://your-frontend-ip/pages/auth/activate.html?uidb64={uid}&token={token}"  # frontend link.
            send_mail(  # sends email.
                'Activate Your Account',  # subject.
                f'Click here: {activation_link}',  # body.
                settings.DEFAULT_FROM_EMAIL,  # from email.
                [instance.email],  # to email.
            )
        if getattr(settings, 'TESTING', False):  # checks if in test mode.
            send_email_task()  # runs directly in tests.
        else:
            django_rq.enqueue(send_email_task)  # queues normally.