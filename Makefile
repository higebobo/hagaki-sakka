CSS_DIR=assets/scss
CSS_DIR=../../static/css
PY_DIR=${HOME}/.virtualenv/py33
PY2_DIR=${HOME}/.virtualenv/py27

all: run2

clean-css:
	cd ${SCSS_DIR};rm -f *.css

scss: clean-css
	cd ${SCSS_DIR};sass --style compressed style.scss:${CSS_DIR}/style.css

scss-all: scss
	cd ${SCSS_DIR};sass --style compressed normalize.scss:${CSS_DIR}/normalize.min.css
	cd ${SCSS_DIR};sass --style compressed foundation.scss:${CSS_DIR}/foundation.min.css

run:
	${PY_DIR}/bin/python app.py

run2:
	${PY2_DIR}/bin/python app.py

shell:
	${PY_DIR}/bin/python shell.py

shell2:
	${PY2_DIR}/bin/python shell.py

test:
	${PY_DIR}/bin/nosetests -v *.py

status:
	hg status

commit:
	hg commit -m 'modify'

pull:
	hg pull
	hg update

push:
	hg push

commit-push: commit push

glog:
	hg glog --style compact
