%bcond_without test
%bcond_without bench
%bcond_without backup
# for now defaults to make a Debug build
%bcond_without debug

Name: mariadb
Version: 10.3.14
Release: 0
License: GPLv2
Summary: Open Source Drop-in replacement for MySQL
Url: https://mariadb.org/

Source0: https://downloads.mariadb.org/f/mariadb-%{version}/source/mariadb-%{version}.tar.gz?serve
Patch0: int8.patch
Patch1: msg_dontwait.patch
Patch2: my_ulonglong2double.patch
Patch3: large_file.patch
Patch4: backtrace_symbols_fd.patch
Patch5: openat.patch
Patch6: o_nofollow-and-o_cloexec.patch

BuildRequires: bison
BuildRequires: cmake
BuildRequires: libevent-devel
BuildRequires: zlib-devel
BuildRequires: libncurses6
BuildRequires: openssl-devel
BuildRequires: libutil-devel
BuildRequires: libxml2-devel
BuildRequires: libstdcplusplus-devel

%description
MariaDB is an enhanced, drop-in replacement for MySQL. MariaDB is used because it is fast, scalable and robust, with a rich ecosystem of storage engines, plugins and many other tools make it very versatile for a wide variety of use cases.

%package server
Summary: The MariaDB server and related files

%description server
MariaDB is a multi-user, multi-threaded SQL database server. It is a
client/server implementation consisting of a server daemon (mysqld)
and many different client programs and libraries. This package contains
the MariaDB server and some accompanying files and directories.
MariaDB is a community developed branch of MySQL.

%package  devel
Summary: Files for development of MariaDB/MySQL applications

%description devel
MariaDB is a multi-user, multi-threaded SQL database server.
MariaDB is a community developed branch of MySQL.

This package contains everything needed for developing MariaDB/MySQL client
and server applications.

%if %{with backup}
%package backup
Summary: The mariabackup tool for physical online backups

%description backup
MariaDB Backup is an open source tool provided by MariaDB for performing
physical online backups of InnoDB, Aria and MyISAM tables.
For InnoDB, "hot online" backups are possible.
%endif

%if %{with test}
%package test
Summary: The test suite distributed with MariaDB

%description test
This package contains the regression test suite distributed with the MariaDB
sources.
%endif

%if %{with bench}
%package bench
Summary: MariaDB benchmark scripts and data

%description bench
This package contains benchmark scripts and data for use when benchmarking
MariaDB.
%endif

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

# generic build instructions https://mariadb.com/kb/en/library/generic-build-instructions/
%build

# cleanup to use proper binaries
find . -type f | xargs perl -p -i -e 's|/usr/bin/perl|%{_bindir}/perl|g;s|#!/bin/sh|#!/QOpenSys/usr/bin/sh|g'

export LDFLAGS=-Wl,-brtl,-bbigtoc,-blibpath:/QOpenSys/pkgs/lib:/QOpenSys/usr/lib,-lutil
export CFLAGS="${CFLAGS:--O2 -g -maix64}"

export CXXFLAGS="${CXXFLAGS:--O2 -g -maix64}"
export FFLAGS="${FFLAGS:--O2 -g -maix64}"

# TODO investigate adding odbc support for connect plugin
# might just need adding build requires of unix odbc

cmake -LAH  -DCMAKE_INSTALL_PREFIX="%{_prefix}" \
    -DINSTALL_LIBDIR="%{_libdir}" \
    -DINSTALL_INCLUDEDIR="include/%{name}" \
    -DINSTALL_SYSCONFDIR="%{_sysconfdir}/%{name}" \
    -DINSTALL_SYSCONF2DIR="%{_sysconfdir}/%{name}" \
    -DINSTALL_INFODIR="%{_infodir}" \
    -DINSTALL_DOCDIR="%{_datadir}/doc/%{name}" \
    -DINSTALL_DOCREADMEDIR="%{_datadir}/doc/%{name}" \
    -DINSTALL_BINDIR="%{_bindir}" \
    -DINSTALL_SBINDIR="%{_prefix}/sbin" \
    -DINSTALL_MANDIR="%{_mandir}" \
    -DINSTALL_PLUGINDIR="%{_libdir}/%{name}/plugin" \
    -DINSTALL_MYSQLSHAREDIR="%{_datadir}/%{name}" \
    -DINSTALL_MYSQLTESTDIR=%{?with_test:share/mysql-test}%{!?with_test:} \
    -DINSTALL_SQLBENCHDIR="%{_datadir}" \
    -DINSTALL_SHAREDIR="%{_datadir}" \
    -DINSTALL_SCRIPTDIR="%{_bindir}" \
    -DINSTALL_SUPPORTFILESDIR="%{_datadir}/%{name}" \
    -DMYSQL_DATADIR="/QOpenSys/var/lib/%{name}/data" \
    -DCMAKE_CXX_COMPILER="%{_bindir}/g++" \
    -DCMAKE_BUILD_TYPE=%{?with_debug:Debug}%{!?with_debug:MinSizeRel} \
    -DWITH_ZLIB=system \
    -DWITH_LIBEVENT=system \
    -DWITH_JEMALLOC=no \
    -DWITH_SSL=system \
    -DWITH_SYSTEMD=no \
    -DWITH_MARIABACKUP=%{?with_backup:ON}%{!?with_backup:NO} \
    -DWITHOUT_MROONGA=1 \
    -DWITH_UNIT_TESTS=NO \
    -DPLUGIN_AUTH_PAM=NO \
    -DPLUGIN_AWS_KEY_MANAGEMENT=NO \
    -DCONNECT_WITH_MONGO=OFF \
    -DCONNECT_WITH_JDBC=OFF \
    -DCONNECT_WITH_ODBC=OFF \
    -DHAVE_POSIX_FALLOCATE=0 \
    -DHAVE_BACKTRACE_SYMBOLS_FD=0 \

# hack -- removes all -Werror that get appended to c/cxx flags when making a debug build
# only use this for -DCMAKE_BUILD_TYPE=Debug
%if %{with debug}
find . -name flags.make | xargs perl -p -i -e 's|-Werror||g'
%endif

VERBOSE=1 %make_build

%install
%make_install

# when not building with bench
%if %{with_bench} < 1
rm -r %{buildroot}%{_datadir}/sql-bench
%endif

# we are not building with embeded server
rm %{buildroot}%{_mandir}/man1/mysql_client_test_embedded.1
rm %{buildroot}%{_mandir}/man1/mysql_embedded.1
rm %{buildroot}%{_mandir}/man1/mysqltest_embedded.1

# when not building with embeded rocksdb
rm %{buildroot}%{_mandir}/man1/mysql_ldb.1*

rm %{buildroot}%{_mandir}/man1/tokuft_logprint.1
rm %{buildroot}%{_mandir}/man1/tokuftdump.1

# default cnf folder for configs
mkdir  %{buildroot}/%{_sysconfdir}/%{name}/my.cnf.d
# default data dir for msqld
mkdir -p  %{buildroot}/QOpenSys/var/lib/%{name}/data

# need to open up my.cnf and edit /etc/my.cnf.d to /QOpenSys/etc/mariadb/my.cnf.d
perl -p -i -e 's|/etc/my.cnf.d|%{_sysconfdir}/%{name}/my.cnf.d|g' %{buildroot}/%{_sysconfdir}/%{name}/my.cnf

# need to set lc-messages-dir
cat <<EOF >> %{buildroot}/%{_sysconfdir}/%{name}/my.cnf

[mariadb]
lc_messages_dir=/QOpenSys/pkgs/share/mariadb/
EOF

# test
%check
#cd %{buildroot}/%{_datadir}/mysql-test
#./mysql-test-run.pl \
#    --suite-timeout=720 \
#    --ssl
#    --force
#    --max-test-fail=0
#    --testcase-timeout=30 \
#    --shutdown-timeout=60 \
#echo "done with mysql-test"

# client package
%files
%defattr(-, qsys, *none)
%{_bindir}/msql2mysql
%{_bindir}/mysql
%{_bindir}/mysql_find_rows
%{_bindir}/mysql_plugin
%{_bindir}/mysql_waitpid
%{_bindir}/mysqlaccess
%{_bindir}/mysqladmin
%{_bindir}/mysqlbinlog
%{_bindir}/mysqlcheck
%{_bindir}/mysqldump
%{_bindir}/mysqlimport
%{_bindir}/mysqlshow
%{_bindir}/mysqlslap


%{_mandir}/man1/msql2mysql.1*
%{_mandir}/man1/mysql.1*
%{_mandir}/man1/mysql_find_rows.1*
%{_mandir}/man1/mysql_plugin.1*
%{_mandir}/man1/mysql_waitpid.1*
%{_mandir}/man1/mysqlaccess.1*
%{_mandir}/man1/mysqladmin.1*
%{_mandir}/man1/mysqlbinlog.1*
%{_mandir}/man1/mysqlcheck.1*
%{_mandir}/man1/mysqldump.1*
%{_mandir}/man1/mysqlimport.1*
%{_mandir}/man1/mysqlshow.1*
%{_mandir}/man1/mysqlslap.1*

%{_sysconfdir}/%{name}/client.cnf
%{_sysconfdir}/%{name}/mysql-clients.cnf
# should be in common package
%{_datadir}/%{name}/charsets


%files server
%defattr(-, qsys, *none)
%{_bindir}/aria_chk
%{_bindir}/aria_dump_log
%{_bindir}/aria_ftdump
%{_bindir}/aria_pack
%{_bindir}/aria_read_log
%{_bindir}/innochecksum
%{_bindir}/myisamchk
%{_bindir}/myisam_ftdump
%{_bindir}/myisamlog
%{_bindir}/myisampack
%{_bindir}/my_print_defaults
%{_bindir}/mysql_install_db
%{_bindir}/mysql_secure_installation
%{_bindir}/mysql_tzinfo_to_sql
%{_bindir}/mysqld_safe
%{_bindir}/mysqld_safe_helper
%{_bindir}/replace
%{_bindir}/resolve_stack_dump
%{_bindir}/resolveip
%{_bindir}/wsrep_sst_common
%{_bindir}/wsrep_sst_mariabackup
%{_bindir}/wsrep_sst_mysqldump
%{_bindir}/wsrep_sst_rsync
%{_bindir}/wsrep_sst_rsync_wan

%{_prefix}/sbin/mysqld
%{_mandir}/man8/mysqld.8*


# server-utils
%{_bindir}/mysql_convert_table_format
%{_bindir}/mysql_fix_extensions
%{_bindir}/mysql_setpermission
%{_bindir}/mysql_upgrade
%{_bindir}/mysqld_multi
%{_bindir}/mysqldumpslow
%{_bindir}/mysqlhotcopy
%{_bindir}/mytop
%{_bindir}/perror


# TODO clean up and %{?with_foo} for each plugin
%{_libdir}/%{name}/plugin/*

%{_mandir}/man1/aria_chk.1*
%{_mandir}/man1/aria_dump_log.1*
%{_mandir}/man1/aria_ftdump.1*
%{_mandir}/man1/aria_pack.1*
%{_mandir}/man1/aria_read_log.1*
%{_mandir}/man1/galera_new_cluster.1*
%{_mandir}/man1/galera_recovery.1*
%{_mandir}/man1/innochecksum.1*
%{_mandir}/man1/mariadb-service-convert.1*
%{_mandir}/man1/my_print_defaults.1*
%{_mandir}/man1/myisam_ftdump.1*
%{_mandir}/man1/myisamchk.1*
%{_mandir}/man1/myisamlog.1*
%{_mandir}/man1/myisampack.1*
%{_mandir}/man1/mysql.server.1*
%{_mandir}/man1/mysql_install_db.1*
%{_mandir}/man1/mysql_secure_installation.1*
%{_mandir}/man1/mysql_tzinfo_to_sql.1*
%{_mandir}/man1/mysqld_safe.1*
%{_mandir}/man1/mysqld_safe_helper.1*
%{_mandir}/man1/replace.1*
%{_mandir}/man1/resolve_stack_dump.1*
%{_mandir}/man1/resolveip.1*
%{_mandir}/man1/wsrep_*.1*

# server-utils 
%{_mandir}/man1/mysql_convert_table_format.1*
%{_mandir}/man1/mysql_fix_extensions.1*
%{_mandir}/man1/mysql_setpermission.1*
%{_mandir}/man1/mysql_upgrade.1*
%{_mandir}/man1/mysqldumpslow.1*
%{_mandir}/man1/mysqld_multi.1*
%{_mandir}/man1/mysqlhotcopy.1*
%{_mandir}/man1/perror.1*

# errmsgs
%{_datadir}/%{name}/errmsg-utf8.txt
%{_datadir}/%{name}/czech/errmsg.sys
%{_datadir}/%{name}/danish/errmsg.sys
%{_datadir}/%{name}/dutch/errmsg.sys
%{_datadir}/%{name}/english/errmsg.sys
%{_datadir}/%{name}/estonian/errmsg.sys
%{_datadir}/%{name}/french/errmsg.sys
%{_datadir}/%{name}/german/errmsg.sys
%{_datadir}/%{name}/greek/errmsg.sys
%{_datadir}/%{name}/hindi/errmsg.sys
%{_datadir}/%{name}/hungarian/errmsg.sys
%{_datadir}/%{name}/italian/errmsg.sys
%{_datadir}/%{name}/japanese/errmsg.sys
%{_datadir}/%{name}/korean/errmsg.sys
%{_datadir}/%{name}/norwegian/errmsg.sys
%{_datadir}/%{name}/norwegian-ny/errmsg.sys
%{_datadir}/%{name}/polish/errmsg.sys
%{_datadir}/%{name}/portuguese/errmsg.sys
%{_datadir}/%{name}/romanian/errmsg.sys
%{_datadir}/%{name}/russian/errmsg.sys
%{_datadir}/%{name}/serbian/errmsg.sys
%{_datadir}/%{name}/slovak/errmsg.sys
%{_datadir}/%{name}/spanish/errmsg.sys
%{_datadir}/%{name}/swedish/errmsg.sys
%{_datadir}/%{name}/ukrainian/errmsg.sys

%{_datadir}/%{name}/fill_help_tables.sql
%{_datadir}/%{name}/install_spider.sql
%{_datadir}/%{name}/maria_add_gis_sp.sql
%{_datadir}/%{name}/maria_add_gis_sp_bootstrap.sql
%{_datadir}/%{name}/mysql_performance_tables.sql
%{_datadir}/%{name}/mysql_system_tables.sql
%{_datadir}/%{name}/mysql_system_tables_data.sql
%{_datadir}/%{name}/mysql_test_data_timezone.sql
%{_datadir}/%{name}/mysql_test_db.sql
%{_datadir}/%{name}/mysql_to_mariadb.sql
%{_datadir}/%{name}/wsrep.cnf
%{_datadir}/%{name}/wsrep_notify
%{_datadir}/%{name}/mysql-log-rotate

#figure where proper package for these
%{_datadir}/doc/%{name}/COPYING
%{_datadir}/doc/%{name}/COPYING.thirdparty
%{_datadir}/doc/%{name}/CREDITS
%{_datadir}/doc/%{name}/EXCEPTIONS-CLIENT
%{_datadir}/doc/%{name}/INSTALL-BINARY
%{_datadir}/doc/%{name}/README-wsrep
%{_datadir}/doc/%{name}/README.md

# candidates for removal
%{_datadir}/%{name}/mysql.server
%{_datadir}/%{name}/mysqld_multi.server
%{_datadir}/%{name}/magic
%{_datadir}/%{name}/policy/apparmor/README
%{_datadir}/%{name}/policy/apparmor/usr.sbin.mysqld
%{_datadir}/%{name}/policy/apparmor/usr.sbin.mysqld.local
%{_datadir}/%{name}/policy/selinux/README
%{_datadir}/%{name}/policy/selinux/mariadb-server.fc
%{_datadir}/%{name}/policy/selinux/mariadb-server.te
%{_datadir}/%{name}/policy/selinux/mariadb.te
%{_datadir}/%{name}/binary-configure

%{_sysconfdir}/%{name}/enable_encryption.preset
%{_sysconfdir}/%{name}/init.d/mysql
%{_sysconfdir}/%{name}/logrotate.d/mysql
%{_sysconfdir}/%{name}/server.cnf
%{_sysconfdir}/%{name}/my.cnf

%dir %{_sysconfdir}/%{name}/my.cnf.d
%dir /QOpenSys/var/lib/%{name}/data

%files devel
%defattr(-, qsys, *none)
%{_includedir}/%{name}/*
%{_libdir}/libmariadb.so
%{_libdir}/libmariadbclient.a
%{_libdir}/libmysqlclient.a
%{_libdir}/libmysqlclient.so
%{_libdir}/libmysqlclient_r.a
%{_libdir}/libmysqlclient_r.so
%{_libdir}/libmysqlservices.a

# Do we really need the following?
%{_libdir}/pkgconfig/libmariadb.pc
%{_datadir}/pkgconfig/mariadb.pc

%{_datadir}/aclocal/mysql.m4

%{_bindir}/mysql_config
%{_bindir}/mariadb_config
%{_mandir}/man1/mysql_config*

%if %{with backup}
%files backup
%{_bindir}/mariabackup
%{_bindir}/mbstream
%{_mandir}/man1/mariabackup.1*
%{_mandir}/man1/mbstream.1*
%endif

%if %{with test}
%files test
%defattr(-, qsys, *none)
%{_datadir}/mysql-test/*
# consider removing
%{_prefix}/data/test/db.opt

%{_bindir}/mysql_client_test
%{_bindir}/mysqltest
%{_mandir}/man1/mysql_client_test.1*
%{_mandir}/man1/my_safe_process.1*
%{_mandir}/man1/mysqltest.1*
%{_mandir}/man1/mysql-stress-test.pl.1*
%{_mandir}/man1/mysql-test-run.pl.1*
%endif

%if %{with bench}
%files bench
%defattr(-, qsys, *none)
%{_datadir}/sql-bench/*
%endif

%changelog
