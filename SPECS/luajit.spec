Name:       luajit
Version:    2.0.2
Release:    0%{?dist}
Summary:    Just-In-Time Compiler for Lua
License:    MIT
URL:        http://luajit.org/
Source0:    http://luajit.org/download/LuaJIT-%{version}.tar.gz

%define debug_package %{nil}

%description
LuaJIT implements the full set of language features defined by Lua 5.1.
The virtual machine is API- and ABI-compatible to the standard
Lua interpreter and can be deployed as a drop-in replacement.

%prep
%setup -q -n LuaJIT-%{version}

%build
make amalg PREFIX=%{_prefix} TARGET_STRIP=@: \
           CFLAGS='%{optflags} -DLUAJIT_ENABLE_LUA52COMPAT'

%install
%make_install PREFIX=%{_prefix} INSTALL_LIB=%{buildroot}%{_libdir}
mv -T %{buildroot}%{_bindir}/luajit-%{version} %{buildroot}%{_bindir}/luajit
# Add binfmt_misc configuration to binfmt.d(5) directory
mkdir -p %{buildroot}%{_prefix}/lib/binfmt.d
echo ':luajit:M::\x1b\x4c\x4a::%{_bindir}/luajit:' > \
      %{buildroot}%{_prefix}/lib/binfmt.d/luajit.conf

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%doc COPYRIGHT README doc/*
%{_bindir}/luajit
%{_mandir}/man1/luajit.1.gz
%{_prefix}/lib/binfmt.d/luajit.conf
%{_libdir}/libluajit-5.1.so.*
%{_datadir}/%{name}-%{version}/jit/*.lua
%dir %{_datadir}/%{name}-%{version}
%dir %{_datadir}/%{name}-%{version}/jit
%{_libdir}/libluajit-5.1.a
%{_libdir}/libluajit-5.1.so
%{_libdir}/pkgconfig/luajit.pc
%{_includedir}/luajit-2.0/*.h*
