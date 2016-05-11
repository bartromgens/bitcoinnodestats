

from nodedata.models import create_node_data
from datetime import datetime

from django_cron import CronJobBase, Schedule


class UpdateNodeData(CronJobBase):
    RUN_EVERY_MINS = 5
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'nodedata.create_node_data'    # a unique code

    def do(self):
        create_node_data()


class TestUpdateNode(CronJobBase):
    RUN_EVERY_MINS = 5
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'nodedata.test_create_node_data'

    def do(self):
        print('start TestUpdateNode::do()')
        print('timestamp: ' + str(datetime.now()))
        create_node_data()
