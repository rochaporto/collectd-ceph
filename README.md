collectd-ceph
==================

## Overview

A set of collectd plugins monitoring and publishing metrics for Ceph components.

## Requirements

It assumes an existing installation of [collectd](http://collectd.org/documentation.shtml).

Check its documentation for details.

## Setup and Configuration

The example configuration(s) below assume the plugins to be located under `/usr/lib/collectd/plugins/ceph`.

If you're under ubuntu, consider installing from [this ppa](https://launchpad.net/~rocha-porto/+archive/collectd).

Each plugin should have its own config file, under `/etc/collectd/conf.d/<pluginname>.conf`, which
should follow some similar to:
```
# cat /etc/collectd/conf.d/ceph_health.conf

<LoadPlugin "python">
    Globals true
</LoadPlugin>

<Plugin "python">
    ModulePath "/usr/lib/collectd/plugins/ceph"

    Import "ceph_health_plugin"

    <Module "ceph_health_plugin">
        Verbose "False"
    </Module>
</Plugin>
```

### Puppet

If you use puppet for configuration, then try this excelent [collectd](https://github.com/pdxcat/puppet-module-collectd) module.

It has plenty of docs on how to use it, but for our specific plugins:
```
  collectd::plugin::python { 'ceph_health':
    modulepath => '/usr/lib/collectd/plugins/ceph',
    module     => 'ceph_health_plugin',
    config     => {
      'Verbose'    => 'true',
    },
  }
```

## Limitations

The debian packaging files are provided, but don't expect the deb in the official repos.

## Development

All contributions more than welcome, just send pull requests.

## License

GPLv2 (check LICENSE).

## Contributors

Ricardo Rocha <ricardo@catalyst.net.nz>

## Support

Please log tickets and issues at the [github home](https://github.com/rochaporto/collectd-ceph/issues).

## Additional Notes

### Ubuntu Packaging

[These instructions](http://packaging.ubuntu.com/html/packaging-new-software.html) should give full details.

In summary, do this once to prepare your environment:
```
pbuilder-dist precise create
```

and for every release (from master):
```
mkdir /tmp/build-collectd-os
cd /tmp/build-collectd-os
wget https://github.com/rochaporto/collectd-ceph/archive/master.zip
unzip master.zip
tar zcvf collectd-ceph-0.1.tar.gz collectd-ceph-master/
bzr dh-make collectd-ceph 0.1 collectd-ceph-0.1.tar.gz
cd collectd-ceph
bzr builddeb -S
cd ../build-area
pbuilder-dist precise build collectd-ceph_0.1-1ubuntu1.dsc
dput ppa:rocha-porto/collectd ../collectd-ceph_0.1-1ubuntu1_source.changes
```
