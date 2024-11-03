@echo off
pip install build twine
python -m build
twine upload --repository pypi dist/*
rd /s /q dist
for /f %%i in ('dir /ad /b /w *.egg-info') do rd /s /q %%i
