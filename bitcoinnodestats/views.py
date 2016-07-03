from datetime import datetime
import pytz

from django.views.generic import TemplateView
from django.http.response import HttpResponseRedirect

from nodedata.models import RawNodeData, NodeStats, Node


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = NodeStats(
            bin_size_hour=24,
            date_begin=datetime(2009, 1, 3),
            date_end=datetime.now(tz=pytz.utc)
        )
        context['node'] = Node()
        return context


class PlotsViews(TemplateView):
    template_name = "plots.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
