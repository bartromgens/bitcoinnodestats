from django.test import TestCase

from nodedata.models import RawNodeData, create_node_data

import bitcoin.rpc


class TestNodeData(TestCase):

    def test_create_node_data(self):
        proxy = bitcoin.rpc.Proxy()
        info = proxy.getinfo()
        nettotals = proxy.call('getnettotals')

        nodedata = create_node_data()

        conncount = info['connections']
        sent_bytes = nettotals['totalbytessent']
        received_bytes = nettotals['totalbytesrecv']

        self.assertTrue(RawNodeData.objects.filter(id=nodedata.id))
        nodedata = RawNodeData.objects.get(id=nodedata.id)
        self.assertEqual(nodedata.get_connection_count(), conncount)
        self.assertEqual(nodedata.get_sent_bytes(), sent_bytes)
        self.assertEqual(nodedata.get_received_bytes(), received_bytes)