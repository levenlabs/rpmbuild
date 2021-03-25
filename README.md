# rpmbuild

Our rpmbuild repo for rpms we have built. You can check out all the options for
rpms to be built in the `SPECS` folder, and build any of them by doing:

```shell
docker run --rm -it -v ${PWD}:/root/rpmbuild centos:7 /bin/bash
# From inside docker image
yum update -y
yum groupinstall -y 'Development Tools'
yum install -y rpmdevtools yum-utils centos-release-scl
cd /root/rpmbuild
spectool -g -C ./SOURCES SPECS/whatever.spec
yum-builddep -y SPECS/whatever.spec
rm -rf /tmp/rpmbuild
rpmbuild --define "_topdir `pwd`" --define "_builddir /tmp/rpmbuild/build" --define "_buildrootdir /tmp/rpmbuild/buildroot" -ba SPECS/whatever.spec
```
