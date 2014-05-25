# Ubuntu Packaging

[These instructions](http://packaging.ubuntu.com/html/packaging-new-software.html) should give full details.

In summary, do this once to prepare your environment:
```
pbuilder-dist precise create
```

and for every release (from master):
```
rm -rf /tmp/build-collectd
mkdir /tmp/build-collectd
cd /tmp/build-collectd
wget https://github.com/rochaporto/collectd-ceph/archive/master.zip
unzip master.zip
tar zcvf collectd-ceph-0.2.0.tar.gz collectd-ceph-master/
bzr dh-make collectd-ceph 0.2.0 collectd-ceph-0.2.0.tar.gz
cd collectd-ceph
bzr builddeb -S
cd ../build-area
pbuilder-dist precise build collectd-ceph_0.2.0-1ubuntu1.dsc
dput ppa:rocha-porto/collectd ../collectd-ceph_0.2.0-1ubuntu1_source.changes
```
