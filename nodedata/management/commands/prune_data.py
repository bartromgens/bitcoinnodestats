from django.core.management.base import BaseCommand, CommandError
from nodedata.models import RawNodeData

from datetime import timedelta


class Command(BaseCommand):
    help = 'Removes'

    # def add_arguments(self, parser):
    #     parser.add_argument('poll_id', nargs='+', type=int)

    def handle(self, *args, **options):
        min_time_diff = timedelta(hours=1)
        datapoints = RawNodeData.objects.values('id', 'datetime_created')
        if not datapoints:
            print('WARNING: no data points found!')
            return
        time_previous = datapoints[0]['datetime_created']
        delete_ids = []
        for datapoint in datapoints:
            timediff = datapoint['datetime_created'] - time_previous
            if timediff < min_time_diff:
                print('remove point: ' + str(datapoint['id']))
                delete_ids.append(datapoint['id'])
                # point_to_remove.delete()
            else:
                time_previous = datapoint['datetime_created']
                print('keep point: ' + str(datapoint['id']))
        print('START: delete ' + str(len(delete_ids)) + ' model(s) from database')
        print('START: this may take several minutes')
        RawNodeData.objects.filter(id__in=delete_ids).delete()
        print('END: delete models from database')
