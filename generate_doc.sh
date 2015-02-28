#!/usr/bin/env bash
pycco *.py -d ./
mv *.html ../dialog_doc/
rm pycco.css
pyreverse -f 'ALL' -m y -o png -p Dialog *
mv *.png ../dialog_doc/