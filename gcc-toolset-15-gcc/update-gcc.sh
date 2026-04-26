#!/bin/sh
# https://src.fedoraproject.org/rpms/gcc/blob/f43/f/update-gcc.sh

if [ "$#" -eq 0 ]; then
  echo "Usage: ./update-gcc.sh"
  exit 1
fi
export LC_ALL=C
if ! [ -f SPECS/gcc-toolset-15-gcc.spec ]; then echo Must be run in the directory with SPECS/gcc-toolset-15-gcc.spec file.; exit 1; fi
if [ -d gcc-dir.tmp ]; then echo gcc-dir.tmp already exists.; exit 1; fi
v=`sed -n 's/^%global gcc_version //p' SPECS/gcc-toolset-15-gcc.spec`
p=`sed -n 's/^%global gitrev //p' SPECS/gcc-toolset-15-gcc.spec`
git clone https://gcc.gnu.org/git/gcc.git gcc-dir.tmp
git --git-dir=gcc-dir.tmp/.git fetch origin $p
d=`sed -n 's/^%%global DATE //p' SPECS/gcc-toolset-15-gcc.spec`
git --git-dir=gcc-dir.tmp/.git archive --prefix=gcc-$v-$d/ $p | xz -9e > gcc-$v-$d.tar.xz
rm -rf gcc-dir.tmp
