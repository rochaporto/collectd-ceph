#!/usr/bin/env python
#
# vim: tabstop=4 shiftwidth=4

# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; only version 2 of the License is applicable.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# Authors:
#   Ricardo Rocha <ricardo@catalyst.net.nz>
#
# About this plugin:
#   This plugin collects information regarding Ceph OSDs.
#
# collectd:
#   http://collectd.org
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
# ceph osds:
#   http://ceph.com/docs/master/rados/operations/monitoring/#checking-osd-status
#

import collectd
import json
import traceback
import subprocess

import base

class CephOsdPlugin(base.Base):

    def __init__(self):
        base.Base.__init__(self)
        self.prefix = 'ceph'

    def get_stats(self):
        """Retrieves stats from ceph osds"""

        ceph_cluster = "%s-%s" % (self.prefix, self.cluster)

        data = { ceph_cluster: { 
            'pool': { 'number': 0 },
            'osd': { 'up': 0, 'in': 0, 'down': 0, 'out': 0} 
        } }
        output = None
        try:
            cephosdcmdline='ceph osd dump --format json --cluster ' + self.cluster
            output = subprocess.check_output(cephosdcmdline, shell=True)
        except Exception as exc:
            collectd.error("ceph-osd: failed to ceph osd dump :: %s :: %s"
                    % (exc, traceback.format_exc()))
            return

        if output is None:
            collectd.error('ceph-osd: failed to ceph osd dump :: output was None')

        json_data = json.loads(output)

        # number of pools
        data[ceph_cluster]['pool']['number'] = len(json_data['pools'])

        # pool metadata
        for pool in json_data['pools']:
            pool_name = "pool-%s" % pool['pool_name']
            data[ceph_cluster][pool_name] = {}
            data[ceph_cluster][pool_name]['size'] = pool['size']
            data[ceph_cluster][pool_name]['pg_num'] = pool['pg_num']
            data[ceph_cluster][pool_name]['pgp_num'] = pool['pg_placement_num']

        osd_data = data[ceph_cluster]['osd']
        # number of osds in each possible state
        for osd in json_data['osds']:
            if osd['up'] == 1:
                osd_data['up'] += 1
            else:
                osd_data['down'] += 1
            if osd['in'] == 1:
                osd_data['in'] += 1
            else:
                osd_data['out'] += 1
    
        return data

try:
    plugin = CephOsdPlugin()
except Exception as exc:
    collectd.error("ceph-osd: failed to initialize ceph osd plugin :: %s :: %s"
            % (exc, traceback.format_exc()))

def configure_callback(conf):
    """Received configuration information"""
    plugin.config_callback(conf)

def read_callback():
    """Callback triggerred by collectd on read"""
    plugin.read_callback()

collectd.register_config(configure_callback)
collectd.register_read(read_callback, plugin.interval)

