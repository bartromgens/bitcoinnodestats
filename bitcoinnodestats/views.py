from datetime import datetime, timedelta
import pytz

from django.views.generic import TemplateView
from django.http.response import HttpResponseRedirect

from nodedata.models import RawNodeData, NodeStats, Node
from nodedata.models import create_data_record


class HomeView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        bin_size_hour = 6
        date_begin = datetime.utcnow() - timedelta(days=30)
        date_end = datetime.now(tz=pytz.utc)

        if 'date_begin' in self.request.GET:
            date_begin = datetime.strptime(self.request.GET['date_begin'], "%Y-%m-%d")
        if 'date_end' in self.request.GET:
            date_end = datetime.strptime(self.request.GET['date_end'], "%Y-%m-%d")
        if 'bin_size_hour' in self.request.GET:
            bin_size_hour = int(self.request.GET['bin_size_hour'])

        context = super().get_context_data(**kwargs)

        # generate a new data record on every page load until there are 10 records available for plotting
        if RawNodeData.objects.count() < 10:
            create_data_record()

        if RawNodeData.objects.count() > 1:
            print('node data exists')
            stats = NodeStats(
                bin_size_hour=bin_size_hour,
                date_begin=date_begin,
                date_end=date_end
            )
        else:
            stats = None

        context['stats'] = stats
        context['node'] = Node()
        return context


class PlotsViews(TemplateView):
    template_name = "plots.html"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
