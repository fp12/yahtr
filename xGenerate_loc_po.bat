CALL venv\Scripts\activate.bat

REM Generate main loc template file with keys from code --no-location
python -m tools.pygettext -o data\loc\yahtr.pot yahtr\localization\ids.py

REM Add data localization keys
python -m tools.build_data_loc

pause