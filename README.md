collectd-ceph
==================

## Overview

A set of collectd plugins monitoring and publishing metrics for Ceph components.

## Screenshots

Sample Grafana dashboard displaying common metrics from the plugins:

![image](https://raw.github.com/rochaporto/collectd-ceph/master/public/ceph-overview.png)

## Requirements

It assumes an existing installation of [collectd](http://collectd.org/documentation.shtml) - check docs for details.

## Plugins and Metrics

There are several plugins, usually mapping to the ceph command line tools.

Find below a list of the available plugins and the metrics they publish.

* ceph_monitor_plugin
  * ceph-<cluster>.mon.gauge.number (total number of monitors)
  * ceph-<cluster>.mon.gauge.quorum (number of monitors in quorum)

## Setup and Configuration

The example configuration(s) below assume the plugins to be located under `/usr/lib/collectd/plugins/ceph`.

If you're under ubuntu, consider installing from [this ppa](https://launchpad.net/~rocha-porto/+archive/collectd).

Each plugin should have its own config file, under `/etc/collectd/conf.d/<pluginname>.conf`, which
should follow something similar to:
```
# cat /etc/collectd/conf.d/ceph_pool.conf

<LoadPlugin "python">
    Globals true
</LoadPlugin>

<Plugin "python">
    ModulePath "/usr/lib/collectd/plugins/ceph"

    Import "ceph_pool_plugin"

    <Module "ceph_pool_plugin">
        Verbose "True"
        Cluster "ceph"
        Interval "60"
        TestPool "test"
    </Module>
</Plugin>
```

### Puppet

If you use puppet for configuration, then try this excelent [collectd](https://github.com/pdxcat/puppet-module-collectd) module.

It has plenty of docs on how to use it, but for our specific plugins:
```
  collectd::plugin::python { 'ceph_pool':
    modulepath => '/usr/lib/collectd/plugins/ceph',
    module     => 'ceph_pool_plugin',
    config     => {
      'Verbose'  => 'true',
      'Cluster'  => 'ceph',
      'Interval' => 60,
      'TestPool' => 'test',
    },
  }
```

## Limitations

The debian packaging files are provided, but not yet available in the official repos.

## Development

All contributions more than welcome, just send pull requests.

## License

GPLv2 (check LICENSE).

## Contributors

Ricardo Rocha <ricardo@catalyst.net.nz>

## Support

Please log tickets and issues at the [github home](https://github.com/rochaporto/collectd-ceph/issues).

## Additional Notes

Some [handy instructions][docs/ubuntu.md] on how to build for ubuntu.
