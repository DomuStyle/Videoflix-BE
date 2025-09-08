"""Signal handlers for the auth_app application.

This module defines signals to send activation emails for newly created inactive users,
using Django's signal framework and RQ for asynchronous task queuing.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver 
from django.contrib.auth.models import User
from django.core.mail import send_mail 
from django.conf import settings 
from django.utils.http import urlsafe_base64_encode 
from django.utils.encoding import force_bytes 
from django.contrib.auth.tokens import default_token_generator
import django_rq  


def send_email_task(instance):  
    """Send an account activation email for the given user.

    Args:
        instance: The User instance to send the activation email for.
    """
    uid = urlsafe_base64_encode(force_bytes(instance.pk))  # Encode user ID for URL
    token = default_token_generator.make_token(instance)  # Generate activation token
    frontend_url = 'http://localhost:5500'
    activation_link = f"{frontend_url}/pages/auth/activate.html?uid={uid}&token={token}"  
    send_mail(  
        'Activate Your Account',  
        f'Click here: {activation_link}', 
        settings.DEFAULT_FROM_EMAIL,  
        [instance.email],  
    )

@receiver(post_save, sender=User)  
def send_activation_email(sender, instance, created, **kwargs):
    """Handle post-save signal for User model to queue activation email.

    Args:
        sender: The model class that sent the signal (User).
        instance: The User instance being saved.
        created (bool): True if the instance was newly created.
        **kwargs: Additional signal arguments.
    """ 
    if created and not instance.is_active: 
        if getattr(settings, 'TESTING', False): 
            send_email_task(instance)  # Run synchronously during tests
        else:
            django_rq.enqueue(send_email_task, instance)  # Queue email task asynchronously