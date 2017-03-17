from django.conf import settings

SAVE_PEER_INFO = getattr(settings, 'SAVE_PEER_INFO', False)  # this stores all peer info and may take up a lot of space
BITCOIN_CONF_FILE = getattr(settings, 'BITCOIN_CONF_FILE', '')
