#! /bin/sh
srcpath="$1"
destpath="$1.$2"
rm -f "$destpath"
cp -f "$srcpath" "$destpath"
