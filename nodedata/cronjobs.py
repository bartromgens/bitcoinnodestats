

from nodedata.models import create_node_data

from django_cron import CronJobBase, Schedule


class UpdateNodeData(CronJobBase):
    schedule = Schedule()
    code = 'nodedata.create_node_data'    # a unique code

    def do(self):
        create_node_data()
