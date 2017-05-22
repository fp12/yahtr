CALL venv\Scripts\activate.bat
cd yahtr
python tools\build_cython.py build_ext --inplace
pause