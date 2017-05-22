REM Generate main loc template file with keys from code --no-location
C:\Python36\python C:\Python34\Tools\i18n\pygettext.py -o data\loc\yahtr.pot src\localization\ids.py

REM Add data localization keys
cd src\
C:\Python36\python -m tools.build_data_loc

pause