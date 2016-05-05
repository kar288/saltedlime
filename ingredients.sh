cat clean.txt | sort | uniq -c | sort -n | awk '{if ($1 > 7) {print $0}}' > ingredients.txt &&
sed -i.bak '/zest$/d' ingredients.txt &&
sed -i.bak '/grated$/d' ingredients.txt &&
sed -i.bak '/large$/d' ingredients.txt &&
sed -i.bak '/to taste$/d' ingredients.txt &&
sed -i.bak '/chopped$/d' ingredients.txt &&
sed -i.bak '/round$/d' ingredients.txt &&
sed -i.bak '/medium$/d' ingredients.txt &&
sed -i.bak '/[0-9] green$/d' ingredients.txt 
