%define openssl_version 1.1.1k

Name: redis
Version: 6.2.1
Release: 1%{dist}
Summary: A persistent key-value database
License: BSD
URL: http://redis.io

Source: http://download.redis.io/releases/%{name}-%{version}.tar.gz
Source1: redis.service
Source100: https://www.openssl.org/source/openssl-%{openssl_version}.tar.gz

BuildRequires: gcc
BuildRequires: devtoolset-8-toolchain
BuildRequires: devtoolset-8-libatomic-devel
BuildRequires: procps-ng
BuildRequires: tcl
BuildRequires: pkgconfig(libsystemd)
BuildRequires: systemd
BuildRequires: which
Requires(postun): systemd

%description
redis is an advanced key-value store

%prep
%setup -q -n redis-%{version}

sed -i -e 's|^dir .*$|dir %{_sharedstatedir}/redis|g' %{_builddir}/redis-%{version}/redis.conf

mkdir %{_builddir}/openssl && tar zxf %{SOURCE100} -C %{_builddir}/openssl --strip-components 1 && cd %{_builddir}/openssl && ./config --prefix=%{_builddir}/redis-%{version}/deps/openssl no-shared no-threads enable-tls1_3 && make && make install_sw LIBDIR=lib

sed -i 's;-lssl;%{_builddir}/redis-%{version}/deps/openssl/lib/libssl.a;g' %{_builddir}/redis-%{version}/src/Makefile
sed -i 's;-lcrypto;%{_builddir}/redis-%{version}/deps/openssl/lib/libcrypto.a;g' %{_builddir}/redis-%{version}/src/Makefile

%global make_flags LDFLAGS="%{?__global_ldflags} -I%{_builddir}/redis-%{version}/deps/openssl/lib" CFLAGS+="%{optflags} -fPIC -I%{_builddir}/redis-%{version}/deps/openssl/include" INSTALL="install -p" PREFIX=%{buildroot}%{_prefix} BUILD_TLS=yes USE_SYSTEMD=yes
: %{make_flags}


%build
source /opt/rh/devtoolset-8/enable
make %{make_flags}

%install
source /opt/rh/devtoolset-8/enable
make %{make_flags} install

install -d %{buildroot}%{_sysconfdir}/redis
install -d %{buildroot}%{_unitdir}
install -d %{buildroot}%{_libdir}/redis
install -d %{buildroot}%{_libdir}/redis/modules
install -d %{buildroot}%{_sharedstatedir}/redis
install -d %{buildroot}%{_localstatedir}/run/redis
install -d %{buildroot}%{_includedir}
install -m 0644 redis.conf %{buildroot}%{_sysconfdir}/redis/redis.conf
install -m 0644 sentinel.conf %{buildroot}%{_sysconfdir}/redis/sentinel.conf
install -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/redis.service
install -m 0644 src/redismodule.h %{buildroot}%{_includedir}/redismodule.h

chmod 755 %{buildroot}%{_bindir}/redis-*

%check
# https://github.com/redis/redis/issues/1417
taskset -c 1 make %{make_flags} test
make %{make_flags} test-sentinel

%files
%defattr(-,root,root)
%dir %{_sysconfdir}/redis
%config(noreplace) %{_sysconfdir}/redis/redis.conf
%config(noreplace) %{_sysconfdir}/redis/sentinel.conf
%{_unitdir}/redis.service
%dir %{_libdir}/redis
%dir %{_libdir}/redis/modules
%dir %{_sharedstatedir}/redis
%dir %{_localstatedir}/run/redis
%{_bindir}/redis-*
%{_includedir}/redismodule.h

%clean
%{__rm} -rf %{buildroot}

%pre
getent group redis >/dev/null || groupadd -r redis
getent passwd redis >/dev/null || \
    useradd -r -g redis -s /sbin/nologin \
    -d %{_sharedstatedir}/redis -c "redis user" redis
exit 0

%post
chown redis:redis %{_sharedstatedir}/redis
chown redis:redis %{_localstatedir}/run/redis
chown redis:redis %{_libdir}/redis
chown redis:redis %{_libdir}/redis/modules

%postun
if [ $1 -eq 2 ]; then
    systemctl daemon-reload >/dev/null 2>&1
fi
