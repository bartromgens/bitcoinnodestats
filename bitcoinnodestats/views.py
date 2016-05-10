from django.views.generic import TemplateView
from django.http.response import HttpResponseRedirect

from nodedata.models import RawNodeData, NodeStats, Node


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = NodeStats()
        context['node'] = Node()
        return context


class PlotsViews(TemplateView):
    template_name = "plots.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
