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


def create_data_record():
    nodedata = create_node_data()
    create_peers(nodedata.peerinfo_json)


def create_node_data(save=True):
    nodedata = RawNodeData()
    try:
        proxy = bitcoin.rpc.Proxy(btc_conf_file=local_settings.BITCOIN_CONF_FILE)
        nodedata.info_json = proxy.getinfo()
        nodedata.nettotals_json = proxy.call('getnettotals')
        nodedata.peerinfo_json = proxy.call('getpeerinfo')
        nodedata.networkinfo_json = proxy.call('getnetworkinfo')
    except (ConnectionRefusedError, bitcoin.rpc.JSONRPCError) as error:
        print(error)
        nodedata.node_up = False
    except FileNotFoundError as error:
        print(error)
        nodedata.node_up = False
    if save:
        nodedata.save()
    else:
        nodedata.datetime_created = timezone.now()
    return nodedata


def create_peers(peerinfo_json):
    for peer_json in peerinfo_json:
        port = peer_json['addr'].split(':')[-1]
        ip = peer_json['addr'].replace(':' + port, '')
        peers = Peer.objects.filter(ip=ip, port=port)
        if not peers.exists():
            peer = peers[0]
        else:
            peer = Peer()
            peer.port = port
            peer.ip = ip
            peer.save()


class RawNodeData(models.Model):
    info_json = JSONField()
    nettotals_json = JSONField()
    peerinfo_json = JSONField()
    networkinfo_json = JSONField()
    node_up = models.BooleanField(default=True, blank=False)
    datetime_created = models.DateTimeField(auto_now_add=True, blank=False)

    def __str__(self):
        return 'RawNodeData: ' + str(self.datetime_created) + ', connections: ' + str(self.get_connection_count())

    def get_sent_bytes(self):
        if not self.nettotals_json:
            print('Warning: nettotals_json is empty')
            return 0
        return self.nettotals_json['totalbytessent']

    def get_received_bytes(self):
        if not self.nettotals_json:
            print('Warning: nettotals_json is empty')
            return 0
        return self.nettotals_json['totalbytesrecv']

    def get_connection_count(self):
        if not self.info_json:
            return 0
        return self.info_json['connections']

    def get_errors(self):
        if not self.info_json:
            return 'Connection Error'
        return self.info_json['errors']

    def get_version(self):
        if not self.networkinfo_json:
            print('Warning: networkinfo_json is empty')
            return '000000'
        return self.networkinfo_json['version']

    def get_version_str(self):
        version_split = re.findall('..', str(self.get_version()))
        minor_version = version_split[1].strip("0")
        if minor_version == '':
            minor_version = '0'
        return 'v0.' + version_split[0] + '.' + minor_version

    def get_subversion_str(self):
        if not self.networkinfo_json:
            print('Warning: networkinfo_json is empty')
            return 'unknown'
        return self.networkinfo_json['subversion'].strip("/")

    def get_time_millis(self):
        if not self.nettotals_json:
            print('Warning: nettotals_json is empty')
            return 0
        return self.nettotals_json['timemillis']  # Unix epoch time in milliseconds according to the operating system’s clock (not the node adjusted time)

    def get_block_count(self):
        if not self.info_json:
            print('Warning: info_json is empty')
            return 0
        return self.info_json['blocks']

    def get_localaddresses(self):
        if not self.nettotals_json:
            print('Warning: nettotals_json is empty')
            return 'unknown'
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
        current_data = create_node_data(save=False)
        self.version = current_data.get_version_str()
        self.subversion = current_data.get_subversion_str()
        self.block_count = current_data.get_block_count()
        self.status = 'Status Unknown'
        self.peers = Node.create_peerinfo(current_data.peerinfo_json)
        self.status = Node.determine_status()

    @staticmethod
    def create_peerinfo(peerinfo_json):
        peers = []
        for peer in peerinfo_json:
            duration = datetime.now(tz=pytz.utc) - datetime.fromtimestamp(peer['conntime'], tz=pytz.utc)
            duration_hours = duration.total_seconds() / 3600.0
            port = peer['addr'].split(':')[-1]
            bitnodes_url = None
            if port == '8333':
                bitnodes_url = 'https://bitnodes.21.co/nodes/' + peer['addr'].replace(':', '-')
            peers.append({
                'duration_hours': duration_hours,
                'address': peer['addr'],
                'bitnodes_url': bitnodes_url,
                'received_mb': peer['bytesrecv'] /1024/1024,
                'sent_mb': peer['bytessent'] /1024/1024,
            })
        return peers

    @staticmethod
    def determine_status():
        try:
            proxy = bitcoin.rpc.Proxy(btc_conf_file=local_settings.BITCOIN_CONF_FILE)
            bestblockhash = proxy.getbestblockhash()
            proxy.call('getblock', b2lx(bestblockhash))
            return 'Up and running'
        except (ConnectionRefusedError, bitcoin.rpc.JSONRPCError) as error:
            print(error)
            return 'Error: Connection Refused'
        except FileNotFoundError as error:
            print(error)
            return 'Error: bitcoin config file not found'


class NodeStats(object):
    max_points = 60

    def __init__(self):
        super().__init__()
        data_latest = RawNodeData.get_latest_node_data()
        self.current_data = create_node_data(save=False)
        self.latest_data_point = data_latest.datetime_created
        self.first_data_point = RawNodeData.get_first_node_data().datetime_created
        self.deltatime_sec = (self.latest_data_point - self.first_data_point).total_seconds()
        assert self.deltatime_sec > 0
        self.connection_count = self.current_data.get_connection_count()
        self.total_sent_bytes = 0
        self.total_received_bytes = 0
        self.generate_stats()
        self.sent_gb = self.total_sent_bytes/1024/1024/1024
        self.received_gb = self.total_received_bytes/1024/1024/1024
        self.share_ratio = 0.0
        if self.received_gb != 0:
            self.share_ratio = self.sent_gb / self.received_gb
        self.n_data_points = RawNodeData.objects.count()

    def generate_stats(self):
        datapoints = RawNodeData.objects.all().order_by('datetime_created')
        datapoints = list(datapoints)
        datapoints.append(self.current_data)
        self.total_sent_bytes = 0
        self.total_received_bytes = 0
        json_points_sent = []
        json_points_received= []
        json_points_upload = []
        json_points_download = []
        json_connection_count = []

        time_bin_size_sec = self.deltatime_sec / self.max_points
        assert time_bin_size_sec > 0

        index = 0
        while index < len(datapoints)-1:
            index += 1
            current_point = datapoints[index-1]
            next_point = datapoints[index]

            time_diff_sec = (next_point.datetime_created - current_point.datetime_created).total_seconds()
            while time_diff_sec < time_bin_size_sec and index < len(datapoints)-1:
                index += 1
                next_point = datapoints[index]
                time_diff_sec = (next_point.datetime_created - current_point.datetime_created).total_seconds()
            sent_diff_bytes = next_point.get_sent_bytes() - current_point.get_sent_bytes()
            received_diff_bytes = next_point.get_received_bytes() - current_point.get_received_bytes()
            if sent_diff_bytes > 0 and received_diff_bytes > 0:
                self.total_sent_bytes += sent_diff_bytes
                self.total_received_bytes += received_diff_bytes
            else:  # the node had a restart
                print('node restarted')
                sent_diff_bytes = 0
                received_diff_bytes = 0

            datetime_local = timezone.localtime(next_point.datetime_created).strftime('%Y-%m-%d %H:%M:%S')
            json_points_sent.append({
                'datetime': datetime_local,
                'y': self.total_sent_bytes / 1024/1024/1024,
            })
            json_points_received.append({
                'datetime': datetime_local,
                'y': self.total_received_bytes / 1024/1024/1024,
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
                'y': next_point.get_connection_count(),
            })

        json_data = {
            'points': json_points_sent,
            'xlabel': 'Time',
            'ylabel': 'Data [GiB]',
            'title': 'Total Outgoing Data',
            'unit': 'GiB'
        }
        NodeStats.write_json(json_data, 'data_sent.json')

        json_data = {
            'points': json_points_received,
            'xlabel': 'Time',
            'ylabel': 'Data [GiB]',
            'title': 'Total Incoming Data',
            'unit': 'GiB'
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
            'unit': 'connections'
        }
        NodeStats.write_json(json_data, 'connections.json')

    @staticmethod
    def write_json(json_data, filename):
        filepath = os.path.join(local_settings.MEDIA_ROOT, filename)
        with open(filepath, 'w') as fileout:
            json.dump(json_data, fileout, indent=4, sort_keys=True)
