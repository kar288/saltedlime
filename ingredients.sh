cat clean.txt | sort | uniq -c | sort -n | awk '{if ($1 > 7) {print $0}}' > ingredients.txt & rm clean.txt &&
python manage.py shell < ingredients2.py
