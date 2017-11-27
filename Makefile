APP_DIR=app
SCSS_DIR=assets/scss
CSS_DIR=../../app/static/css
PYTHON=`which python`
PY_BABEL=`which pybabel`

all: run

run:
	$(PYTHON) manage.py runserver

shell:
	$(PYTHON) manage.py shell.py

test:
	$(PYTHON) manage.py test

clean-css:
	cd ${SCSS_DIR};rm -f *.css

scss: clean-css
	cd ${SCSS_DIR};sass --style compressed style.scss:${CSS_DIR}/style.css

scss-all: scss
	cd ${SCSS_DIR};sass --style compressed normalize.scss:${CSS_DIR}/normalize.min.css
	cd ${SCSS_DIR};sass --style compressed foundation.scss:${CSS_DIR}/foundation.min.css

babel-update:
	cd ${APP_DIR};$(BABEL) extract -F translations/babel.cfg -k lazy_gettext -o translations/messages.pot . && $(BABEL)  update -i translations/messages.pot -d translations

babel-compile:
	cd ${APP_DIR};$(BABEL) compile -d translations

status:
	git status

add:
	git add .

commit: add
	git commit -m 'modify'

pull:
	git pull
	git update

push:
	git push -u origin master

commit-push: commit push
