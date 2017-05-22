REM Generate main loc template file with keys from code --no-location
C:\Python36\python C:\Python36\Tools\i18n\pygettext.py -o data\loc\yahtr.pot yahtr\localization\ids.py

REM Add data localization keys
CALL venv\Scripts\activate.bat
cd yahtr\
python -m tools.build_data_loc

pause