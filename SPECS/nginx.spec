%define nginx_home %{_localstatedir}/cache/nginx
%define nginx_user nginx
%define nginx_group nginx

%define main_version 1.18.0
%define main_release 2%{?dist}.levenlabs

%define openssl_version 1.1.1k
%define pcre_version 8.44
%define zlib_version 1.2.11
%define nginx_more_headers_version 0.33

%define WITH_CC_OPT $(echo %{optflags} $(pcre-config --cflags)) -fPIC
%define WITH_LD_OPT -Wl,-z,relro -Wl,-z,now -pie
%define bdir %{_builddir}/%{name}-%{main_version}

Summary: High performance web server
Name: nginx
Version: %{main_version}
Release: %{main_release}
Vendor: Nginx, Inc.
URL: http://nginx.org/

Source0: http://nginx.org/download/%{name}-%{version}.tar.gz
Source1: nginx-logrotate
Source3: nginx.sysconf
Source4: nginx.conf
Source5: nginx-default.conf
Source8: nginx.service
Source90: https://github.com/openresty/headers-more-nginx-module/archive/v%{nginx_more_headers_version}/headers-more-nginx-module-%{nginx_more_headers_version}.tar.gz
Source100: https://www.openssl.org/source/openssl-%{openssl_version}.tar.gz
Source101: https://ftp.pcre.org/pub/pcre/pcre-%{pcre_version}.tar.gz
Source102: https://www.zlib.net/zlib-%{zlib_version}.tar.gz

License: 2-clause BSD-like license
Group: System Environment/Daemons

BuildRequires: git
BuildRequires: gcc
BuildRequires: perl
BuildRequires: GeoIP-devel
Requires: GeoIP
Requires(pre): shadow-utils
Provides: webserver

%define debug_package %{nil}

%description
nginx [engine x] is an HTTP and reverse proxy server

%prep
%setup -q
tar xf %{SOURCE90} -C %{_builddir}

git clone https://github.com/vozlt/nginx-module-vts %{_builddir}/nginx-module-vts
cd %{_builddir}/nginx-module-vts && git submodule update --init

git clone https://github.com/google/ngx_brotli %{_builddir}/ngx_brotli
cd %{_builddir}/ngx_brotli && git submodule update --init

mkdir %{_builddir}/openssl && tar zxf %{SOURCE100} -C %{_builddir}/openssl --strip-components 1
mkdir %{_builddir}/pcre && tar zxf %{SOURCE101} -C %{_builddir}/pcre --strip-components 1
mkdir %{_builddir}/zlib && tar zxf %{SOURCE102} -C %{_builddir}/zlib --strip-components 1

%build
./configure \
    --prefix=%{_sysconfdir}/nginx \
    --sbin-path=%{_sbindir}/nginx \
    --modules-path=%{_libdir}/nginx/modules \
    --conf-path=%{_sysconfdir}/nginx/nginx.conf \
    --error-log-path=%{_localstatedir}/log/nginx/error.log \
    --http-log-path=%{_localstatedir}/log/nginx/access.log \
    --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp \
    --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp \
    --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp \
    --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp \
    --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp \
    --pid-path=%{_localstatedir}/run/nginx.pid \
    --lock-path=%{_localstatedir}/run/nginx.lock \
    --user=%{nginx_user} \
    --group=%{nginx_group} \
    --with-debug \
    --with-file-aio \
    --with-threads \
    --with-http_addition_module \
    --with-http_auth_request_module \
    --with-http_dav_module \
    --with-http_degradation_module \
    --with-http_flv_module \
    --with-http_geoip_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_mp4_module \
    --with-http_random_index_module \
    --with-http_realip_module \
    --with-http_secure_link_module \
    --with-http_slice_module \
    --with-http_ssl_module \
    --with-http_stub_status_module \
    --with-http_sub_module \
    --with-http_v2_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-pcre \
    --with-pcre-jit \
    --with-stream \
    --with-stream_ssl_module \
    --with-openssl=%{_builddir}/openssl --with-openssl-opt=enable-tls1_3 \
    --with-stream_ssl_preread_module \
    --with-pcre=%{_builddir}/pcre \
    --with-pcre-opt='-g -Ofast -fPIC -m64 -march=native -fstack-protector-strong -D_FORTIFY_SOURCE=2' \
    --with-zlib=%{_builddir}/zlib \
    --with-zlib-opt='-g -Ofast -fPIC -m64 -march=native -fstack-protector-strong -D_FORTIFY_SOURCE=2' \
    --add-module=%{_builddir}/nginx-module-vts \
    --with-cc-opt="%{WITH_CC_OPT}" \
    --with-ld-opt="%{WITH_LD_OPT}" \
    --add-module=%{_builddir}/headers-more-nginx-module-%{nginx_more_headers_version} \
    --add-module=%{_builddir}/ngx_brotli \

make %{?_smp_mflags}

%install
%{__rm} -rf %{buildroot}
%{__make} DESTDIR=%{buildroot} install

%{__mkdir} -p %{buildroot}%{_datadir}/nginx
%{__mv} %{buildroot}%{_sysconfdir}/nginx/html %{buildroot}%{_datadir}/nginx/

%{__rm} -f %{buildroot}%{_sysconfdir}/nginx/*.default
%{__rm} -f %{buildroot}%{_sysconfdir}/nginx/fastcgi.conf

%{__mkdir} -p %{buildroot}%{_localstatedir}/log/nginx
%{__mkdir} -p %{buildroot}%{_localstatedir}/run/nginx
%{__mkdir} -p %{buildroot}%{_localstatedir}/cache/nginx
%{__mkdir} -p %{buildroot}%{_datadir}/nginx/modules
cd %{buildroot}%{_sysconfdir}/nginx && \
    %{__ln_s} ../..%{_libdir}/nginx/modules modules && cd -

%{__mkdir} -p %{buildroot}%{_datadir}/doc/%{name}-%{main_version}
%{__install} -m 644 -p LICENSE \
    %{buildroot}%{_datadir}/doc/%{name}-%{main_version}/COPYRIGHT

%{__mkdir} -p %{buildroot}%{_sysconfdir}/nginx/conf.d
%{__rm} %{buildroot}%{_sysconfdir}/nginx/nginx.conf
%{__install} -m 644 -p %{SOURCE4} \
    %{buildroot}%{_sysconfdir}/nginx/nginx.conf
# we don't need default.conf
# %{__install} -m 644 -p %{SOURCE5} \
#    %{buildroot}%{_sysconfdir}/nginx/conf.d/default.conf

%{__mkdir} -p %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 644 -p %{SOURCE3} \
    %{buildroot}%{_sysconfdir}/sysconfig/nginx

%{__install} -p -D -m 0644 %{bdir}/objs/nginx.8 \
    %{buildroot}%{_mandir}/man8/nginx.8

# install log rotation stuff
%{__mkdir} -p %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -m 644 -p %{SOURCE1} \
   %{buildroot}%{_sysconfdir}/logrotate.d/nginx

# install systemd-specific files
%{__mkdir} -p %{buildroot}%{_unitdir}
%{__install} -m644 %SOURCE8 \
    %{buildroot}%{_unitdir}/nginx.service

%check
%{__rm} -rf %{buildroot}/usr/src

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root)

%{_sbindir}/nginx

%dir %{_sysconfdir}/nginx
%dir %{_sysconfdir}/nginx/conf.d
%{_sysconfdir}/nginx/modules

%config(noreplace) %{_sysconfdir}/nginx/nginx.conf
# %config(noreplace) %{_sysconfdir}/nginx/conf.d/default.conf
%config(noreplace) %{_sysconfdir}/nginx/mime.types
%config(noreplace) %{_sysconfdir}/nginx/fastcgi_params
%config(noreplace) %{_sysconfdir}/nginx/scgi_params
%config(noreplace) %{_sysconfdir}/nginx/uwsgi_params
%config(noreplace) %{_sysconfdir}/nginx/koi-utf
%config(noreplace) %{_sysconfdir}/nginx/koi-win
%config(noreplace) %{_sysconfdir}/nginx/win-utf

%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%config(noreplace) %{_sysconfdir}/sysconfig/nginx

%dir %{_datadir}/nginx
%dir %{_datadir}/nginx/html
%{_datadir}/nginx/html/*
%{_unitdir}/nginx.service

%attr(0755,nginx,nginx) %dir %{_localstatedir}/cache/nginx
%attr(0755,nginx,nginx) %dir %{_localstatedir}/log/nginx

%dir %{_datadir}/doc/%{name}-%{main_version}
%doc %{_datadir}/doc/%{name}-%{main_version}/COPYRIGHT
%{_mandir}/man8/nginx.8*

%pre
# Add the "nginx" user
getent group %{nginx_group} >/dev/null || groupadd -r %{nginx_group}
getent passwd %{nginx_user} >/dev/null || \
    useradd -r -g %{nginx_group} -s /sbin/nologin \
    -d %{nginx_home} -c "nginx user"  %{nginx_user}
exit 0

%post
    # Touch and set permisions on default log files on installation
    if [ -d %{_localstatedir}/log/nginx ]; then
        if [ ! -e %{_localstatedir}/log/nginx/access.log ]; then
            touch %{_localstatedir}/log/nginx/access.log
            %{__chmod} 644 %{_localstatedir}/log/nginx/access.log
            %{__chown} %{nginx_user}:%{nginx_group} %{_localstatedir}/log/nginx/access.log
        fi

        if [ ! -e %{_localstatedir}/log/nginx/error.log ]; then
            touch %{_localstatedir}/log/nginx/error.log
            %{__chmod} 644 %{_localstatedir}/log/nginx/error.log
            %{__chown} %{nginx_user}:%{nginx_group} %{_localstatedir}/log/nginx/error.log
        fi
    fi

    systemctl preset nginx.service

%preun
if [ $1 -eq 0 ]; then
    systemctl --no-reload disable nginx.service >/dev/null 2>&1
    systemctl stop nginx.service >/dev/null 2>&1
fi

%postun
if [ $1 -eq 2 ]; then
    systemctl daemon-reload >/dev/null 2>&1
fi
