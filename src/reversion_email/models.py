"""Database models used by django-reversion."""

import warnings

from reversion.models import Version
from django.conf import settings
from django.db.models import signals
    
def send_diff_to_email(sender, instance, **kwargs):
    from reversion.helpers import generate_patch_html
    versions = sender.objects.filter(content_type=instance.content_type, object_id=instance.object_id).order_by('-id')
    patch = ''
    for field in instance.content_type.model_class()._meta.fields:
        if versions.count()>1:
            patch += "<p><strong>%s</strong>: %s</p>" % ( field.name, generate_patch_html(versions[1],versions[0],field.name) )
        else:
            patch += "<p><strong>%s</strong>: %s</p>" % (field.name, getattr(versions[0], field.name))

    email = EmailMultiAlternatives(
        subject = settings.EMAIL_SUBJECT_PREFIX + instance.revision.comment,
        body = patch, 
        from_email = settings.SERVER_EMAIL, 
        to = [
            i[1] for i in settings.MODERATORS
        ],
    )
    email.attach_alternative(patch, "text/html")
    email.send()

if hasattr(settings,'MODERATORS'):
    signals.post_save.connect(send_diff_to_email, sender = Version)
