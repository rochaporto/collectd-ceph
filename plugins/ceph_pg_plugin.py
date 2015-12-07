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
#   This plugin collects information regarding Ceph Placement Groups (PGs).
#
# collectd:
#   http://collectd.org
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
#

import collectd
import json
import traceback
import subprocess

import base

class CephPGPlugin(base.Base):

    def __init__(self):
        base.Base.__init__(self)
        self.prefix = 'ceph'

    def get_stats(self):
        """Retrieves stats from ceph pgs"""

        ceph_cluster = "%s-%s" % (self.prefix, self.cluster)

        data = { ceph_cluster: { 'pg': { } }  }
        output = None
        try:
            cephpg_cmdline='ceph pg dump --format json --cluster '+ self.cluster
            output = subprocess.check_output(cephpg_cmdline, shell=True)
        except Exception as exc:
            collectd.error("ceph-pg: failed to ceph pg dump :: %s :: %s"
                    % (exc, traceback.format_exc()))
            return

        if output is None:
            collectd.error('ceph-pg: failed to ceph osd dump :: output was None')

        json_data = json.loads(output)

        pg_data = data[ceph_cluster]['pg']
        # number of pgs in each possible state
        for pg in json_data['pg_stats']:
            for state in pg['state'].split('+'):
                if not pg_data.has_key(state):
                    pg_data[state] = 0
                pg_data[state] += 1
    
        # osd perf data
        for osd in json_data['osd_stats']:
            osd_id = "osd-%s" % osd['osd']
            data[ceph_cluster][osd_id] = {}
            data[ceph_cluster][osd_id]['kb_used'] = osd['kb_used']
            data[ceph_cluster][osd_id]['kb_total'] = osd['kb']
            data[ceph_cluster][osd_id]['snap_trim_queue_len'] = osd['snap_trim_queue_len']
            data[ceph_cluster][osd_id]['num_snap_trimming'] = osd['num_snap_trimming']
            data[ceph_cluster][osd_id]['apply_latency_ms'] = osd['fs_perf_stat']['apply_latency_ms']
            data[ceph_cluster][osd_id]['commit_latency_ms'] = osd['fs_perf_stat']['commit_latency_ms']

        return data

try:
    plugin = CephPGPlugin()
except Exception as exc:
    collectd.error("ceph-pg: failed to initialize ceph pg plugin :: %s :: %s"
            % (exc, traceback.format_exc()))

def configure_callback(conf):
    """Received configuration information"""
    plugin.config_callback(conf)

def read_callback():
    """Callback triggerred by collectd on read"""
    plugin.read_callback()

collectd.register_config(configure_callback)
collectd.register_read(read_callback, plugin.interval)

