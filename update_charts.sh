git pull
python beebify.py
git commit -a -m 'Automatically updated charts'
git checkout gh-pages
git checkout master output
git commit -a -m 'Automatically updated charts'
git push
git checkout master
