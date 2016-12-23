#
%define nginx_home %{_localstatedir}/cache/nginx
%define nginx_user nginx
%define nginx_group nginx

%define nginx_echo_version 0.58
%define nginx_more_headers_version 0.29
%define nginx_lua_version 0.10.2
%define nginx_devel_kit_version 0.2.19
%define nginx_rtmp_version 1.1.7

Summary: nginx is a high performance web server
Name: nginx
Version: 1.8.1
Release: 0%{?dist}
Vendor: nginx inc.
URL: http://nginx.org/

Source0: http://nginx.org/download/%{name}-%{version}.tar.gz
Source1: nginx-logrotate
Source2: nginx.conf
Source3: https://github.com/openresty/echo-nginx-module/archive/v%{nginx_echo_version}/echo-nginx-module-%{nginx_echo_version}.tar.gz
Source4: https://github.com/openresty/headers-more-nginx-module/archive/v%{nginx_more_headers_version}/headers-more-nginx-module-%{nginx_more_headers_version}.tar.gz
Source5: https://github.com/openresty/lua-nginx-module/archive/v%{nginx_lua_version}/lua-nginx-module-%{nginx_lua_version}.tar.gz
Source6: https://github.com/simpl/ngx_devel_kit/archive/v%{nginx_devel_kit_version}/ngx_devel_kit-%{nginx_devel_kit_version}.tar.gz
Source7: https://github.com/arut/nginx-rtmp-module/archive/v%{nginx_rtmp_version}/nginx-rtmp-module-%{nginx_rtmp_version}.tar.gz
Source8: nginx-default.conf
Source9: nginx.service

License: 2-clause BSD-like license
Group: System Environment/Daemons

BuildRequires: luajit >= 2.0.2
BuildRequires: zlib-devel
BuildRequires: pcre-devel
BuildRequires: openssl-devel
BuildRequires: perl
BuildRequires: GeoIP-devel
Requires: luajit >= 2.0.2
Requires: openssl >= 1.0.1
Requires: zlib
Requires: pcre
Requires: GeoIP
Requires(pre): shadow-utils
Provides: webserver

%define debug_package %{nil}

%description
nginx [engine x] is an HTTP and reverse proxy server, as well as
a mail proxy server

%prep
%setup -q
tar xf %{SOURCE3} -C $RPM_BUILD_DIR
tar xf %{SOURCE4} -C $RPM_BUILD_DIR
tar xf %{SOURCE5} -C $RPM_BUILD_DIR
tar xf %{SOURCE6} -C $RPM_BUILD_DIR
tar xf %{SOURCE7} -C $RPM_BUILD_DIR

%build
./configure \
    --prefix=%{_sysconfdir}/nginx \
    --sbin-path=%{_sbindir}/nginx \
    --conf-path=%{_sysconfdir}/nginx/nginx.conf \
    --error-log-path=%{_localstatedir}/log/nginx/error.log \
    --http-log-path=%{_localstatedir}/log/nginx/access.log \
    --pid-path=%{_localstatedir}/run/nginx.pid \
    --lock-path=%{_localstatedir}/run/nginx.lock \
    --http-client-body-temp-path=%{_localstatedir}/cache/nginx/client_temp \
    --http-proxy-temp-path=%{_localstatedir}/cache/nginx/proxy_temp \
    --http-fastcgi-temp-path=%{_localstatedir}/cache/nginx/fastcgi_temp \
    --http-uwsgi-temp-path=%{_localstatedir}/cache/nginx/uwsgi_temp \
    --http-scgi-temp-path=%{_localstatedir}/cache/nginx/scgi_temp \
    --user=%{nginx_user} \
    --group=%{nginx_group} \
    --with-http_ssl_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_stub_status_module \
    --with-http_spdy_module \
    --with-http_geoip_module \
    --with-http_auth_request_module \
    --with-mail \
    --with-mail_ssl_module \
    --with-file-aio \
    --with-ipv6 \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
    --with-debug \
    --add-module=$RPM_BUILD_DIR/echo-nginx-module-%{nginx_echo_version} \
    --add-module=$RPM_BUILD_DIR/headers-more-nginx-module-%{nginx_more_headers_version} \
    --add-module=$RPM_BUILD_DIR/lua-nginx-module-%{nginx_lua_version} \
    --add-module=$RPM_BUILD_DIR/ngx_devel_kit-%{nginx_devel_kit_version} \
    --add-module=$RPM_BUILD_DIR/nginx-rtmp-module-%{nginx_rtmp_version}

make %{?_smp_mflags}

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__make} DESTDIR=$RPM_BUILD_ROOT install

%{__mkdir} -p $RPM_BUILD_ROOT%{_datadir}/nginx
%{__mv} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/html $RPM_BUILD_ROOT%{_datadir}/nginx/

%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/log/nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/run/nginx
%{__mkdir} -p $RPM_BUILD_ROOT%{_localstatedir}/cache/nginx

%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/nginx/lua
%{__rm} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/nginx.conf
%{__install} -m 644 -p %{SOURCE2} \
   $RPM_BUILD_ROOT%{_sysconfdir}/nginx/nginx.conf
%{__install} -m 644 -p %{SOURCE8} \
   $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/default.conf

# install log rotation stuff
%{__mkdir} -p $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%{__install} -m 644 -p %{SOURCE1} \
   $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/nginx

# install the service file
%{__mkdir} -p $RPM_BUILD_ROOT%{_unitdir}
%{__install} -m 0644 -p %{SOURCE9} \
    $RPM_BUILD_ROOT%{_unitdir}/nginx.service

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)

%{_sbindir}/nginx

%dir %{_sysconfdir}/nginx
%dir %{_sysconfdir}/nginx/conf.d
%dir %{_sysconfdir}/nginx/lua

%config(noreplace) %{_sysconfdir}/logrotate.d/nginx
%config(noreplace) %{_sysconfdir}/nginx/*

%dir %{_datadir}/nginx
%dir %{_datadir}/nginx/html
%{_datadir}/nginx/html/*
%{_unitdir}/nginx.service

%attr(0755,nginx,nginx) %dir %{_localstatedir}/cache/nginx
%attr(0755,nginx,nginx) %dir %{_localstatedir}/log/nginx

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
