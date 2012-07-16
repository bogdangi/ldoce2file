IFS_OLD=$IFS
IFS=$'\n'
words=`cat $1`
for i in $words
do
    IFS=$IFS_OLD
    ./ldoce2file.py -s -t $2 -w $i
done
