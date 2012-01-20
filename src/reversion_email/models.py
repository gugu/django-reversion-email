"""Database models used by django-reversion-email."""

from reversion.models import Version
from django.conf import settings
from django.db.models import signals
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.core import urlresolvers
from django.contrib.sites.models import Site


def send_diff_to_email(sender, instance, **kwargs):
    from reversion.helpers import generate_patch_html, generate_patch
    versions = sender.objects.filter(content_type=instance.content_type, object_id=instance.object_id).order_by('-id')
    html_template = get_template('reversion_email/email.html')
    text_template = get_template('reversion_email/email.txt')

    patch = []
    object_meta = instance.content_type.model_class()._meta

    for field in object_meta.fields:
        if versions.count() > 1:
            patch.append({ 
                'field' : field.name, 
                'html' : generate_patch_html(versions[1],versions[0],field.name),
                'text' : generate_patch(versions[1],versions[0],field.name) 
            })
        else:
            patch.append({
                'field' : field.name, 
                'html' : getattr(versions[0].object, field.name),
                'text' : getattr(versions[0].object, field.name),
            })

    current_site = Site.objects.get_current()
    url_info = object_meta.app_label, object_meta.module_name,

    context = Context({ 
        'version' : instance, 
        'patch' : patch,
        'site' : current_site, 
        'admin_recover_url' : urlresolvers.reverse('admin:%s_%s_revision'  % url_info, args=[versions[0].object.pk, instance.pk])
    })
    text_content = text_template.render(context)
    html_content = html_template.render(context)

    email = EmailMultiAlternatives(
        subject = settings.EMAIL_SUBJECT_PREFIX + instance.revision.comment,
        body = text_content, 
        from_email = settings.SERVER_EMAIL, 
        to = [
            i[1] for i in settings.MODERATORS
        ],
    )

    email.attach_alternative(html_content, "text/html")
    email.send()

if hasattr(settings,'MODERATORS'):
    signals.post_save.connect(send_diff_to_email, sender = Version)
