from django.views.generic import TemplateView
from django.http.response import HttpResponseRedirect

from nodedata.models import RawNodeData, NodeStats, Node


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_data = RawNodeData.get_latest_node_data()
        context['stats'] = NodeStats()
        context['node'] = Node()
        return context


class DataUsageView(TemplateView):
    template_name = "data_usage_plot.html"

    def get(self, request):
        return super().get(request)
