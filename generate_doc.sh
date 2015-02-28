#!/usr/bin/env bash
pycco *.py -d ../dialog_doc
pyreverse -f 'ALL' -m y -o png -p Dialog *
mv *.png ../dialog_doc/