#!/bin/bash
pyvenv-3.4 --without-pip env
source ./env/bin/activate
curl https://bootstrap.pypa.io/get-pip.py -o - | python3
deactivate
source env/bin/activate
pip3 install ./
easy_install-3.4 pyaudio
pip3 install execnet
wget http://www.abisource.com/downloads/link-grammar/5.2.5/link-grammar-5.2.5.tar.gz
tar -xzf link-grammar-5.2.5.tar.gz
rm link-grammar-5.2.5.tar.gz
cd link-grammar-5.2.5
./configure
make
cp ./link-parser/link-parser ../env/bin/link-parser
cp -r ./link-parser/.libs ../env/bin/.libs
cp -r ./data ../data
cd ..