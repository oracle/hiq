# Run unit tests
Make sure pytest, and coverage packages installed. If not, install it with the following commands:
```
pip3 install pytest
pip3 install coverage
```
Now, in the project hierarchy, change directory to ***tests*** and execute the following commands to run unit tests.
```
coverage run -m pytest test_utils.py
```
Also, to see the test coverage, enter the following commands:
```
coverage html
```
Finally, open the htmlcov/index.html file in your browser, select the utils.py file and view the test coverage.
