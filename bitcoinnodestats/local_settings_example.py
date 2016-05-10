# user settings, included in settings.py
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

ADMINS = (
    ('Your Name', 'email address'),
)

ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Amsterdam'

#STATIC_ROOT = '/home/<username>/webapps/<projectstatic>/'
STATIC_ROOT = ''

# URL prefix for static files.
#STATIC_URL = 'http://www.<your-domain>.com/static/'
STATIC_URL = '/static/'

#MEDIA_ROOT = '/home/<username>/webapps/<projectstatic>/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'bitcoinnodestats/static/media/')

#MEDIA_URL = 'http://www.<your-domain>.com/static/media/'
MEDIA_URL = '/static/media/'


# email server settings for outgoing mails
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.domain.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''

DEFAULT_FROM_EMAIL = 'info@domain.com'
SERVER_EMAIL = 'info@domain.com'
