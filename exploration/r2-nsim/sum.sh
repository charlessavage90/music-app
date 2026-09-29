sum () 
{ 
    for f in "$@";
    do
        echo == $f;
        awk '/^press/{p=1} p && ($1 ~ /^(0|1|3|5|10)$/)' $f.txt;
        grep "routing time" $f.txt;
    done
}
