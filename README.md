# gcc-toolset-15

[manylinux](https://github.com/loong64/manylinux) 项目所需依赖


## Anolis 23(loongarch64)

- https://mirrors.loong64.com/anolis/

```sh
cat > /etc/yum.repos.d/anolis-crb.repo << "EOF"
[crb]
name=AnolisOS $releasever - CRB
baseurl=https://mirrors.loong64.com/anolis/$releasever/Devel/$basearch/os
enabled=1
gpgcheck=0
countme=1
# gpgkey=file:///etc/pki/rpm-gpg/
metadata_expire=86400
enabled_metadata=0

[crb-debuginfo]
name=AnolisOS $releasever - CRB - Debug
baseurl=https://mirrors.loong64.com/anolis/$releasever/Devel/$basearch/debug
enabled=0
gpgcheck=0
# gpgkey=file:///etc/pki/rpm-gpg/
metadata_expire=86400
enabled_metadata=0

[crb-source]
name=AnolisOS $releasever - CRB - Source
baseurl=https://mirrors.loong64.com/anolis/$releasever/Devel/source
enabled=0
gpgcheck=0
# gpgkey=file:///etc/pki/rpm-gpg/
metadata_expire=86400
enabled_metadata=0

EOF
```
```sh
dnf install gcc-toolset-15-binutils gcc-toolset-15-gcc gcc-toolset-15-gcc-c++ gcc-toolset-15-gcc-gfortran gcc-toolset-15-libatomic-devel
```