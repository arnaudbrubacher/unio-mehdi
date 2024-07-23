"""
WSGI config for djui project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
import sys
path = "/var/www/unio_vote/unio"
if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'djui.settings'
os.environ['SETTINGS_MODULE'] = 'djui.settings'
application = get_wsgi_application()
