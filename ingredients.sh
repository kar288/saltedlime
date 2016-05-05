cat clean.txt | sort | uniq -c | sort -n | awk '{if ($1 > 7) {print $0}}' > ingredients.txt & rm clean.txt &&
sed -i.bak '/zest$/d' ingredients.txt &&
sed -i.bak '/grated$/d' ingredients.txt
