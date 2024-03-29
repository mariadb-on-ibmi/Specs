# Specs - build mariadb RPMS for PASE


1) Set up rpm build environment

```bash
export PATH=/QOpenSys/pkgs/bin:$PATH

yum -y install curl rpm-devel rpm-build gcc-aix gzip make-gnu tar-gnu patch-gnu coreutils-gnu git curl gcc-cplusplus-aix

mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SRPMS,SOURCES}
```

2) Clone this repo

```bash
git clone https://github.com/mariadb-on-ibmi/Specs.git
```

3) Get source tarball for your desired version


```bash
pushd ~/rpmbuild/SOURCES

curl -Lk -o mariadb-10.3.14.tar.gz https://downloads.mariadb.org/interstitial/mariadb-10.3.14/source/mariadb-10.3.14.tar.gz/from/http%3A//ftp.hosteurope.de/mirror/archive.mariadb.org/

popd
```

4) Copy the desired spec file and patches into the rpmbuild directory


```bash
cp Specs/10.3.14/mariadb.spec ~/rpmbuild/SPECS

cp Specs/10.3.14/*.patch ~/rpmbuild/SOURCES
```
5) Get build dependencies
```bash
yum-builddep /HOME/QSECOFR/rpmbuild/SPECS/mariadb.spec
```

6) Run the build

```bash
rpmbuild -ba ~/rpmbuild/SPECS/mariadb.spec
```


# Resources

Refer to the [rpm lab](https://github.com/kadler/rpm-lab) for more information on building RPMS for PASE.

