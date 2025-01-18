# signals.py
from django.db.models.signals import post_save,pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Ticket,Technician,CustomUser
from django.contrib import messages
@receiver(post_save, sender=Ticket)
def notify_status_change(sender, instance, **kwargs):
    if instance.status == 'completed':
        send_mail(
            'Ticket Completed',
            f'Ticket "{instance.title}" has been completed.',
            'from@example.com',
            [instance.created_by.user.email, instance.assigned_to.user.email],
            fail_silently=False,
        )
    elif instance.status == 'approved':
        send_mail(
            'Ticket Approved',
            f'Ticket "{instance.title}" has been approved.',
            'from@example.com',
            [instance.created_by.user.email, instance.assigned_to.user.email],
            fail_silently=False,
        )



