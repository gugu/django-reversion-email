django-reversion-email
================

**django-reversion-email** is an extension to django-reversion which sends email notification when model changes

Installation
------------

1. Install `django-reversion` (You can find documentation here: https://github.com/etianen/django-reversion/wiki)
2. Install `google-diff-match-patch` library. It is required for this module. (http://code.google.com/p/google-diff-match-patch/)
2. Add Add `'reversion'` to your `INSTALLED_APPS` setting.
3. Set `'MODERATOR_EMAIL'` in your `settings.py` file.