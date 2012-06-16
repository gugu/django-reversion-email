"""Database models used by django-reversion-email."""

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import NoReverseMatch
from django.template.loader import get_template
from django.template import Context
from django.core import urlresolvers
import difflib


def send_diff_to_email(sender, instance, **kwargs):
    from django.contrib.sites.models import Site
    versions = sender.objects.filter(content_type=instance.content_type, object_id=instance.object_id).order_by('-id')
    html_template = get_template('reversion_email/email.html')
    text_template = get_template('reversion_email/email.txt')

    patch = []
    object_meta = instance.content_type.model_class()._meta
    html_diff = difflib.HtmlDiff()
    text_diff = difflib.Differ()


    for field in object_meta.fields:
        if versions.count() > 1 and (versions[1].object is not None) and (versions[0].object is not None):
            patch.append({ 
                'field' : field.name, 
                'html' : html_diff.make_file([unicode(getattr(versions[1].object, field.name))],[unicode(getattr(versions[0].object,field.name))]),
                'text' : '\n'.join(text_diff.compare([unicode(getattr(versions[1].object, field.name))],[unicode(getattr(versions[0].object,field.name))])),
            })
        elif versions[0].object is not None or versions[1].object is not None:
            patch.append({
                'field' : field.name, 
                'html' : getattr(versions[0].object or versions[1].object, field.name),
                'text' : getattr(versions[0].object or versions[1].object, field.name),
            })

    current_site = Site.objects.get_current()
    url_info = object_meta.app_label, object_meta.module_name,

    context = Context({ 
        'version' : instance, 
        'patch' : patch,
        'site' : current_site, 
    })
    try:
        if len(versions)>1 and (versions[0].object is not None or versions[1].object is not None):
            context['admin_recover_url'] = urlresolvers.reverse('admin:%s_%s_revision'  % url_info, args=[(versions[0].object or versions[1].object).pk, instance.pk])
    except NoReverseMatch:
        pass
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
    from reversion import post_revision_commit, models
    post_revision_commit.connect(send_diff_to_email, sender = models.Version)
