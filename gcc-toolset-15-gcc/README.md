# Anolis OS 23

需要移除 `/usr/lib/rpm/anolis/anolis-annobin-cc1` 文件中 `-fplugin=annobin` 定义

```sh
cat /usr/lib/rpm/anolis/anolis-annobin-cc1

*cc1_options:
+ %{!-fno-use-annobin:%{!iplugindir*:%:find-plugindir()}}
```

需要 `gcc-toolset-15-gcc-plugin-devel` 包
```sh
+ make
Making all in gcc-plugin
make[1]: Entering directory '/root/rpmbuild/BUILD/gcc-15.2.1-20260123/annobin-plugin/annobin-12.93/gcc-plugin'
make all-am
make[2]: Entering directory '/root/rpmbuild/BUILD/gcc-15.2.1-20260123/annobin-plugin/annobin-12.93/gcc-plugin'
CXX annobin.lo
In file included from /opt/rh/gcc-toolset-15/root/usr/lib/gcc/loongarch64-anolis-linux/15/plugin/include/config/loongarch/loongarch-opts.h:28,
from /root/rpmbuild/BUILD/gcc-15.2.1-20260123/obj-loongarch64-anolis-linux/gcc/options.h:8,
from /root/rpmbuild/BUILD/gcc-15.2.1-20260123/obj-loongarch64-anolis-linux/gcc/tm.h:52,
from /root/rpmbuild/BUILD/gcc-15.2.1-20260123/gcc/backend.h:28,
from /root/rpmbuild/BUILD/gcc-15.2.1-20260123/gcc/gcc-plugin.h:30,
from annobin.h:30,
from annobin.cc:21:
/opt/rh/gcc-toolset-15/root/usr/lib/gcc/loongarch64-anolis-linux/15/plugin/include/config/loongarch/loongarch-def.h:51:10: fatal error: loongarch-def-array.h: No such file or directory
51 | #include "loongarch-def-array.h"
| ^~~~~~~~~~~~~~~~~~~~~~~
compilation terminated.
make[2]: *** [Makefile:461: annobin.lo] Error 1
make[2]: Leaving directory '/root/rpmbuild/BUILD/gcc-15.2.1-20260123/annobin-plugin/annobin-12.93/gcc-plugin'
make[1]: *** [Makefile:361: all] Error 2
make[1]: Leaving directory '/root/rpmbuild/BUILD/gcc-15.2.1-20260123/annobin-plugin/annobin-12.93/gcc-plugin'
make: *** [Makefile:429: all-recursive] Error 1
error: Bad exit status from /var/tmp/rpm-tmp.O3B1LJ (%build)
```

需要使用 `QA_RPATHS=$((0x0020))` 进行构建

```sh
QA_RPATHS=$((0x0020)) rpmbuild -ba gcc-toolset-15-gcc.spec
```