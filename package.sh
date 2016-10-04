#!/bin/sh
# note: run clean first
./clean.sh
VERSION=`cat VERSION`
grep $VERSION hs/__init__.py > /dev/null
if [ $? != '0' ]; then
  echo "version mismatch between VERSION and __init__.py"
  exit 1
fi


doZip()
{
TMPTAR=/tmp/tmptar-$TARBASE.tar.gz
tar zcvf $TMPTAR $FILES
mkdir -p build/$TARBASE
cd build/$TARBASE
tar zxvf $TMPTAR
cd ..
zip -r $TARBASE.zip $TARBASE
cd ..
}


doTar()
{
TMPTAR=/tmp/tmptar-$TARBASE.tar.gz
tar zcvf $TMPTAR $FILES
mkdir -p build/$TARBASE
cd build/$TARBASE
tar zxvf $TMPTAR
cd ..
# note: exclude grid.py etc. util it's finished
tar zcvf $TARBASE.tar.gz $TARBASE
cd ..
}

TARBASE=pyhs-$VERSION
FILES="`find . -name '*.py'|grep -v test` README.md"
doTar
doZip
echo The archives have been built in build directory:
ls build


