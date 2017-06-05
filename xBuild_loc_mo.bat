CALL venv\Scripts\activate.bat

REM Processing English...
python -m tools.msgfmt data\loc\yahtr_En.po
REM Processing French...
python -m tools.msgfmt data\loc\yahtr_Fr.po

pause