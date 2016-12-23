# rpmbuild

My rpmbuild repo for rpms I have built for myself for side-projects or for fun.
You can check out all the options for rpms to be built in the `SPECS` folder,
and build any of them by doing:

```
vagrant up
vagrant ssh
# From inside the vagrant box
cd rpmbuild
spectool -g -R SPECS/whatever.spec
rpmbuild -ba SPECS/whatever.spec
```

