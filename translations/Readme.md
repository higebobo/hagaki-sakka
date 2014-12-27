# Using Babel

## Initialize

1. make translation file (message.pot)

     $ ~/.virtualenv/py27/bin/pybabel extract -F translations/babel.cfg -k lazy_gettext -o translations/messages.pot .

2. make message.po

     $ ~/.virtualenv/py27/bin/pybabel init -i translations/messages.pot -d translations -l ja

3. compile

     $ ~/.virtualenv/py27/bin/pybabel compile -d translations
    
## Update

1. extract and update po

     $ ~/.virtualenv/py27/bin/pybabel extract -F translations/babel.cfg -k lazy_gettext -o translations/messages.pot . && ~/.virtualenv/py27/bin/pybabel update -i translations/messages.pot -d translations

2. compile

     $ ~/.virtualenv/py27/bin/pybabel compile -d translations
