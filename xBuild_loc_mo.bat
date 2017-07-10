CALL venv\Scripts\activate.bat

REM Processing English...
python -m tools.msgfmt data\loc\en\LC_MESSAGES\yahtr.po
REM Processing French...
python -m tools.msgfmt data\loc\fr\LC_MESSAGES\yahtr.po

pause