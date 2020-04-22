# rpmbuild

Our rpmbuild repo for rpms we have built. You can check out all the options for
rpms to be built in the `SPECS` folder, and build any of them by doing:

```
vagrant up
vagrant ssh
# From inside the vagrant box
cd rpmbuild
cp -Rf /vagrant/* .
rm -rf BUILD/*
rm -rf SOURCES/*.gz
spectool -g -R SPECS/whatever.spec
rpmbuild -ba SPECS/whatever.spec
```

`vagrant provision` should download all required source files and install all
build dependencies. If any source versions change you'll have to re-run `vagrant provision`.
