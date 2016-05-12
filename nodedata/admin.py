from django.contrib import admin

from .models import RawNodeData, Peer

admin.site.register(RawNodeData)
admin.site.register(Peer)