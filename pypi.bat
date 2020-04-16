python setup.py sdist bdist_wheel
pause
python -m twine upload dist/*
