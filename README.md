# Specs- build mariadb RPMS for PASE


1. Set up rpm build environment

```bash
export PATH=/QOpenSys/pkgs/bin:$PATH

yum install curl rpm-devel rpm-build gcc-aix gzip make-gnu tar-gnu patch-gnu coreutils-gnu git

mkdir -p ~/rpmbuild/{BUILD,BUILDROOT,RPMS,SRPMS,SOURCES}
```

2. Clone this repo

```bash
git clone https://github.com/mariadb-on-ibmi/Specs.git
```

3. Get source tarball for your desired version

For example mariadb 10.3.14

```bash
pushd ~/rpmbuild/SOURCES

curl -OLk https://downloads.mariadb.org/f/mariadb-10.3.14/source/mariadb-10.3.14.tar.gz?serve

popd
```

4. Copy the spec files into the rpmbuild directory 

For example mariadb 10.3.14

```bash
cp Specs/10.3.14/mariadb.spec ~/rpmbuild/SPECS

cp Specs/10.3.14/*.patch ~rpmbuild/SOURCES
```


5. Run the build

```bash
rpmbuild -ba ~/rpmbuild/SPECS/mariadb.spec
```


# Resources

Refer to the [rpm lab](https://github.com/kadler/rpm-lab) for more information on building RPMS for PASE.

