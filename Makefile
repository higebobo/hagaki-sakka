APP_DIR=app
SCSS_DIR=assets/scss
CSS_DIR=../../app/static/css
PY2_HOME=${HOME}/.virtualenv/py27
PY3_HOME=${HOME}/.virtualenv/py33
PYTHON=${PY2_HOME}/bin/python
PY2_BABEL=${PY2_HOME}/bin/pybabel
PY3_BABEL=${PY3_HOME}/bin/pybabel
PY_BABEL=${PY2_BABEL}

all: run

run:
	${PYTHON} manage.py runserver

shell:
	${PYTHON} manage.py shell.py

test:
	${PYTHON} manage.py test

clean-css:
	cd ${SCSS_DIR};rm -f *.css

scss: clean-css
	cd ${SCSS_DIR};sass --style compressed style.scss:${CSS_DIR}/style.css

scss-all: scss
	cd ${SCSS_DIR};sass --style compressed normalize.scss:${CSS_DIR}/normalize.min.css
	cd ${SCSS_DIR};sass --style compressed foundation.scss:${CSS_DIR}/foundation.min.css

babel-update:
	cd ${APP_DIR};${PY_BABEL} extract -F translations/babel.cfg -k lazy_gettext -o translations/messages.pot . && ${PY_BABEL}  update -i translations/messages.pot -d translations

babel-compile:
	cd ${APP_DIR};${PY_BABEL} compile -d translations

status:
	git status

commit:
	git commit -a

pull:
	git pull

push:
	git push origin master

commit-push: commit push
