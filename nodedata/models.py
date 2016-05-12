import os
import json
from datetime import datetime
import re
import pytz

from django.db import models
from django.utils import timezone

from jsonfield import JSONField

import bitcoin.rpc
from bitcoin.core import b2lx

from bitcoinnodestats import local_settings


def create_node_data():
    nodedata = RawNodeData()
    try:
        proxy = bitcoin.rpc.Proxy(btc_conf_file=local_settings.BITCOIN_CONF_FILE)
        nodedata.info_json = proxy.getinfo()
        nodedata.nettotals_json = proxy.call('getnettotals')
        nodedata.peerinfo_json = proxy.call('getpeerinfo')
        nodedata.networkinfo_json = proxy.call('getnetworkinfo')
    except (ConnectionRefusedError, bitcoin.rpc.JSONRPCError) as error:
        print(error)
    nodedata.save()
    for peer_json in nodedata.peerinfo_json:
        port = peer_json['addr'].split(':')[-1]
        ip = peer_json['addr'].replace(':' + port, '')
        peers = Peer.objects.filter(ip=ip, port=port)
        if peers.exists():
            peer = peers[0]
        else:
            peer = Peer()
        peer.port = port
        peer.ip = ip
        peer.save()
    return nodedata


class RawNodeData(models.Model):
    info_json = JSONField()
    nettotals_json = JSONField()
    peerinfo_json = JSONField()
    networkinfo_json = JSONField()
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
        return self.networkinfo_json['version']

    def get_version_str(self):
        version_split = re.findall('..', str(self.get_version()))
        minor_version = version_split[1].strip("0")
        if minor_version == '':
            minor_version = '0'
        return 'v0.' + version_split[0] + '.' + minor_version

    def get_subversion(self):
        return self.networkinfo_json['subversion'].strip("/")

    def get_time_millis(self):
        return self.nettotals_json['timemillis']  # Unix epoch time in milliseconds according to the operating system’s clock (not the node adjusted time)

    def get_blocks(self):
        return self.info_json['blocks']

    def get_localaddresses(self):
        return self.networkinfo_json['localaddresses']

    @staticmethod
    def get_latest_node_data():
        return RawNodeData.objects.all().latest('datetime_created')

    @staticmethod
    def get_first_node_data():
        return RawNodeData.objects.all().earliest('datetime_created')


class Peer(models.Model):
    ip = models.CharField(max_length=300, blank=False)
    port = models.IntegerField(blank=False)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return str(self.ip) + ':' + str(self.port)


class Node(object):
    def __init__(self):
        super().__init__()
        data_latest = RawNodeData.get_latest_node_data()
        self.version = data_latest.get_version_str()
        self.subversion = data_latest.get_subversion()
        self.block_count = data_latest.get_blocks()
        self.peers = []
        for peer in data_latest.peerinfo_json:
            duration = datetime.now(tz=pytz.utc) - datetime.fromtimestamp(peer['conntime'], tz=pytz.utc)
            duration_hours = duration.total_seconds() / 3600.0
            port = peer['addr'].split(':')[-1]
            bitnodes_url = None
            if port == '8333':
                bitnodes_url = 'https://bitnodes.21.co/nodes/' + peer['addr'].replace(':', '-')
            self.peers.append({
                'duration_hours': duration_hours,
                'address': peer['addr'],
                'bitnodes_url': bitnodes_url,
                'received_mb': peer['bytesrecv'] /1024/1024,
                'sent_mb': peer['bytessent'] /1024/1024,
            })
        try:
            proxy = bitcoin.rpc.Proxy(btc_conf_file=local_settings.BITCOIN_CONF_FILE)
            bestblockhash = proxy.getbestblockhash()
            self.best_block = proxy.call('getblock', b2lx(bestblockhash))
            self.status = 'Up and running'
        except (ConnectionRefusedError, bitcoin.rpc.JSONRPCError) as error:
            self.status = 'Error: Connection Refused'
            print(error)


class NodeStats(object):
    time_bin_size_sec = 10*60

    def __init__(self):
        super().__init__()
        data_latest = RawNodeData.get_latest_node_data()
        self.latest_data_point = data_latest.datetime_created
        self.first_data_point = RawNodeData.get_first_node_data().datetime_created
        self.connection_count = data_latest.get_connection_count()
        self.total_sent_bytes = 0
        self.total_received_bytes = 0
        self.generate_stats()
        self.sent_gb = self.total_sent_bytes/1024/1024/1024
        self.received_gb = self.total_received_bytes/1024/1024/1024
        self.share_ratio = self.sent_gb / self.received_gb
        self.n_data_points = RawNodeData.objects.count()

    def generate_stats(self):
        datapoints = RawNodeData.objects.all().order_by('datetime_created')
        datapoints = list(datapoints)
        self.total_sent_bytes = 0
        self.total_received_bytes = 0
        json_points_sent = []
        json_points_received= []
        json_points_upload = []
        json_points_download = []
        json_connection_count = []

        index = 0
        while index < len(datapoints)-1:
            next_point = datapoints[index+1]
            current_point = datapoints[index]

            time_diff_sec = (next_point.get_time_millis() - current_point.get_time_millis()) / 1000
            while time_diff_sec < self.time_bin_size_sec and index < len(datapoints)-2:
                index += 1
                next_point = datapoints[index + 1]
                time_diff_sec = (next_point.get_time_millis() - current_point.get_time_millis()) / 1000
            index += 1
            sent_diff_bytes = next_point.get_sent_bytes() - current_point.get_sent_bytes()
            received_diff_bytes = next_point.get_received_bytes() - current_point.get_received_bytes()
            if sent_diff_bytes < 0 or received_diff_bytes < 0:
                # server restarted, cannot use differences between current and next point
                continue
            self.total_sent_bytes += sent_diff_bytes
            self.total_received_bytes += received_diff_bytes
            datetime_utc = datetime.fromtimestamp(current_point.get_time_millis()/1000, tz=pytz.utc)
            datetime_local = timezone.localtime(datetime_utc).strftime('%Y-%m-%d %H:%M:%S')
            json_points_sent.append({
                'datetime': datetime_local,
                'y': self.total_sent_bytes/1024/1024,
            })
            json_points_received.append({
                'datetime': datetime_local,
                'y': self.total_received_bytes / 1024 / 1024,
            })
            json_points_upload.append({
                'datetime': datetime_local,
                'y': sent_diff_bytes / 1024 / time_diff_sec,
            })
            json_points_download.append({
                'datetime': datetime_local,
                'y': received_diff_bytes / 1024 / time_diff_sec,
            })
            json_connection_count.append({
                'datetime': datetime_local,
                'y': current_point.get_connection_count(),
            })

        json_data = {
            'points': json_points_sent,
            'xlabel': 'Time',
            'ylabel': 'Data [MB]',
            'title': 'Total Outgoing Data',
            'unit': 'MB'
        }
        NodeStats.write_json(json_data, 'data_sent.json')

        json_data = {
            'points': json_points_received,
            'xlabel': 'Time',
            'ylabel': 'Data [MB]',
            'title': 'Total Incoming Data',
            'unit': 'MB'
        }
        NodeStats.write_json(json_data, 'data_received.json')

        json_data = {
            'points': json_points_upload,
            'xlabel': 'Time',
            'ylabel': 'Upload [kB/s]',
            'title': 'Upload Speed',
            'unit': 'kB/s'
        }
        NodeStats.write_json(json_data, 'upload_speed.json')

        json_data = {
            'points': json_points_download,
            'xlabel': 'Time',
            'ylabel': 'Download [kB/s]',
            'title': 'Download Speed',
            'unit': 'kB/s'
        }
        NodeStats.write_json(json_data, 'download_speed.json')

        json_data = {
            'points': json_connection_count,
            'xlabel': 'Time',
            'ylabel': 'Peers [#]',
            'title': 'Peers',
            'unit': ''
        }
        NodeStats.write_json(json_data, 'connections.json')

    @staticmethod
    def write_json(json_data, filename):
        filepath = os.path.join(local_settings.MEDIA_ROOT, filename)
        with open(filepath, 'w') as fileout:
            json.dump(json_data, fileout, indent=4, sort_keys=True)
