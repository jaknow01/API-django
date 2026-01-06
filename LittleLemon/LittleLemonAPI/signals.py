from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group


@receiver(post_save, sender=User)
def assign_default_group(sender, instance, created, **kwargs):
    """Automatycznie przypisuje nowego użytkownika do grupy 'customer'"""
    if created:
        customer_group, _ = Group.objects.get_or_create(name='customer')
        instance.groups.add(customer_group)
