# rpmbuild

Our rpmbuild repo for rpms we have built.  You can check out all the options for
rpms to be built in the `SPECS` folder, and build any of them by doing:

```
vagrant up
vagrant ssh
# From inside the vagrant box
cd rpmbuild
rpmbuild -ba SPECS/whatever.spec
```

`vagrant provision` should download all required source files and install all
build dependencies. If any source versions change you'll have to re-run `vagrant
provision`.

## Nginx

Compiling nginx is still a bit weird, you'll need to first compile and install
the luajit rpm, then redo `vagrant provision`, then do the normal rpmbuild
command.
