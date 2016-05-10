from django.views.generic import TemplateView

from nodedata.models import RawNodeData, NodeStats, Node


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_data = RawNodeData.get_latest_node_data()
        # sent_bytes, received_bytes = RawNodeData.get_total_data_usage_bytes()
        # context['connection_count'] = latest_data.get_connection_count()
        # context['sent_mb'] = sent_bytes/1024/1024
        # context['received_mb'] = received_bytes/1024/1024
        # context['node_version'] = latest_data.get_version()
        context['stats'] = NodeStats()
        context['node'] = Node()
        return context