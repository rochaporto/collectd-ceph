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
#   This plugin evaluates current latency to write to the test pool.
#
# collectd:
#   http://collectd.org
# collectd-python:
#   http://collectd.org/documentation/manpages/collectd-python.5.shtml
# ceph pools:
#   https://ceph.com/docs/master/man/8/rados/#pool-specific-commands
#

import collectd
import traceback
import subprocess

import base

class CephLatencyPlugin(base.Base):

    def __init__(self):
        base.Base.__init__(self)
        self.prefix = 'ceph'

    def get_stats(self):
        """Retrieves stats regarding latency to write to a test pool"""

        ceph_cluster = "%s-%s" % (self.prefix, self.cluster)

        data = { ceph_cluster: {} }

        output = None
        try:
            output = subprocess.check_output(
              "timeout 30s rados -p data bench 10 write -t 1 -b 65536 2>/dev/null | grep -i latency | awk '{print 1000*$3}'", shell=True)
        except Exception as exc:
            collectd.error("ceph-latency: failed to run rados bench :: %s :: %s"
                    % (exc, traceback.format_exc()))
            return

        if output is None:
            collectd.error('ceph-latency: failed to run rados bench :: output was None')

        results = output.split('\n')
        # push values
        data[ceph_cluster]['cluster'] = {}
        data[ceph_cluster]['cluster']['avg_latency'] = results[0]
        data[ceph_cluster]['cluster']['stddev_latency'] = results[1]
        data[ceph_cluster]['cluster']['max_latency'] = results[2]
        data[ceph_cluster]['cluster']['min_latency'] = results[3]

        return data

try:
    plugin = CephLatencyPlugin()
except Exception as exc:
    collectd.error("ceph-latency: failed to initialize ceph latency plugin :: %s :: %s"
            % (exc, traceback.format_exc()))

def configure_callback(conf):
    """Received configuration information"""
    plugin.config_callback(conf)

def read_callback():
    """Callback triggerred by collectd on read"""
    plugin.read_callback()

collectd.register_config(configure_callback)
collectd.register_read(read_callback, plugin.interval)

