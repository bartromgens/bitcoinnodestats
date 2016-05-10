import os
import json
from datetime import datetime

from django.db import models
from bitcoinnodestats import local_settings

from jsonfield import JSONField

import bitcoin.rpc


def create_node_data():
    proxy = bitcoin.rpc.Proxy()
    info = proxy.getinfo()  # https://bitcoin.org/en/developer-reference#getinfo
    nettotals = proxy.call('getnettotals')  # https://bitcoin.org/en/developer-reference#getnettotals

    nodedata = RawNodeData()
    nodedata.info_json = info
    nodedata.nettotals_json = nettotals
    nodedata.save()


class RawNodeData(models.Model):
    info_json = JSONField()
    nettotals_json = JSONField()
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return 'RawNodeData: ' + str(self.datetime_created) + ', connections: ' + str(self.get_connection_count())

    def get_sent_bytes(self):
        return self.nettotals_json['totalbytessent']

    def get_received_bytes(self):
        return self.nettotals_json['totalbytesrecv']

    def get_connection_count(self):
        return self.info_json['connections']

    def get_errors(self):
        return self.info_json['errors']

    def get_version(self):
        return self.info_json['version']

    def get_time_millis(self):
        return self.nettotals_json['timemillis']  # Unix epoch time in milliseconds according to the operating system’s clock (not the node adjusted time)

    @staticmethod
    def get_latest_node_data():
        return RawNodeData.objects.all().latest('datetime_created')


class Node(object):
    def __init__(self):
        super().__init__()
        data_latest = RawNodeData.get_latest_node_data()
        self.version = data_latest.get_version()


class NodeStats(object):
    def __init__(self):
        super().__init__()
        data_latest = RawNodeData.get_latest_node_data()
        self.connection_count = data_latest.get_connection_count()
        self.total_sent_bytes = 0
        self.total_received_bytes = 0
        self.generate_stats()
        self.sent_mb = self.total_sent_bytes/1024/1024
        self.received_mb = self.total_received_bytes/1024/1024
        self.n_data_points = RawNodeData.objects.count()
        self.latest_data_point = data_latest.datetime_created
        NodeStats.create_connections_json()

    def generate_stats(self):
        datapoints = RawNodeData.objects.all().order_by('datetime_created')
        self.total_sent_bytes = 0
        self.total_received_bytes = 0
        json_points_sent = []
        json_points_received= []
        json_points_upload = []
        json_points_download = []
        for i in range(0, datapoints.count()-1):
            next_point = datapoints[i+1]
            current_point = datapoints[i]
            time_diff_sec = (next_point.get_time_millis() - current_point.get_time_millis()) / 1000
            sent_diff_bytes = next_point.get_sent_bytes() - current_point.get_sent_bytes()
            received_diff_bytes = next_point.get_received_bytes() - current_point.get_received_bytes()
            if sent_diff_bytes < 0 or received_diff_bytes < 0:
                print('server was down')
                continue
            self.total_sent_bytes += sent_diff_bytes
            self.total_received_bytes += received_diff_bytes
            json_points_sent.append({
                'datetime': datetime.fromtimestamp(current_point.get_time_millis()/1000).strftime('%Y-%m-%d %H:%M:%S'),
                'y': self.total_sent_bytes/1024/1024,
            })
            json_points_received.append({
                'datetime': datetime.fromtimestamp(current_point.get_time_millis() / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'y': self.total_received_bytes / 1024 / 1024,
            })
            json_points_upload.append({
                'datetime': datetime.fromtimestamp(current_point.get_time_millis() / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'y': sent_diff_bytes / 1024 / time_diff_sec,
            })
            json_points_download.append({
                'datetime': datetime.fromtimestamp(current_point.get_time_millis() / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'y': received_diff_bytes / 1024 / time_diff_sec,
            })

        json_data = {
            'points': json_points_sent,
            'xlabel': 'Time',
            'ylabel': 'Total data sent [MB]',
        }
        NodeStats.write_json(json_data, 'data_sent.json')

        json_data = {
            'points': json_points_received,
            'xlabel': 'Time',
            'ylabel': 'Total data received [MB]',
        }
        NodeStats.write_json(json_data, 'data_received.json')

        json_data = {
            'points': json_points_upload,
            'xlabel': 'Time',
            'ylabel': 'Upload [kB/s]',
        }
        NodeStats.write_json(json_data, 'upload_speed.json')

        json_data = {
            'points': json_points_download,
            'xlabel': 'Time',
            'ylabel': 'Download [kB/s]',
        }
        NodeStats.write_json(json_data, 'download_speed.json')

    @staticmethod
    def create_connections_json():
        datapoints = RawNodeData.objects.all().order_by('datetime_created')
        json_connection_count = []
        for point in datapoints:
            json_connection_count.append({
                'datetime': datetime.fromtimestamp(point.get_time_millis() / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'y': point.get_connection_count(),
            })

        json_data = {
            'points': json_connection_count,
            'xlabel': 'Time',
            'ylabel': 'Connections [-]',
        }
        NodeStats.write_json(json_data, 'connections.json')


    @staticmethod
    def write_json(json_data, filename):
        filepath = os.path.join(local_settings.MEDIA_ROOT, filename)
        with open(filepath, 'w') as fileout:
            json.dump(json_data, fileout, indent=4, sort_keys=True)
