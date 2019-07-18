file=toio-cubes.txt
tmpfile=/tmp/$file.tmp

if (sudo `which python` tomotoio/scanner.py $* > $tmpfile)
then
  if [ -s $tmpfile ]
  then
    [ -f $file ] && cp $file $file.bak
    cp -f $tmpfile $file
    echo Discovered Cubes:
    cat $file
  else
    echo No cubes found.
  fi
else
  cat $tmpfile >&2
fi

rm -f $tmpfile
