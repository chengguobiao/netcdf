PYPREFIX_PATH=/usr
PYTHONLIBS=LD_LIBRARY_PATH=/usr/lib
PYTHONPATH=$(PYPREFIX_PATH)/bin/python  
FIRST_EASYINSTALL=$(PYTHONLIBS) easy_install
PIP=pip
PYTHON=bin/python
EASYINSTALL=bin/easy_install
VIRTUALENV=virtualenv
SOURCE_ACTIVATE=$(PYTHONLIBS) . bin/activate; 

unattended:
	@ (sudo ls 2>&1) >> tracking.log

ubuntu:
	@ (sudo apt-get -y install zlibc curl libssl0.9.8 libbz2-dev libxslt*-dev libxml*-dev 2>&1) >> tracking.log
	@ echo "[ assume       ] ubuntu distribution"

bin/activate: requirements.txt
	@ echo "[ using        ] $(PYTHONPATH)"
	@ echo "[ installing   ] $(VIRTUALENV)"
	@ (sudo $(FIRST_EASYINSTALL) virtualenv 2>&1) >> tracking.log
	@ echo "[ creating     ] $(VIRTUALENV) with no site packages"
	@ ($(PYTHONLIBS) $(VIRTUALENV) --python=$(PYTHONPATH) --no-site-packages . 2>&1) >> tracking.log
	@ echo "[ installing   ] $(PIP) inside $(VIRTUALENV)"
	@ ($(SOURCE_ACTIVATE) $(EASYINSTALL) pip 2>&1) >> tracking.log
	@ ($(SOURCE_ACTIVATE) $(EASYINSTALL) numpy==1.8.0 2>&1) >> tracking.log
	@ echo "[ installing   ] $(PIP) requirements"
	@ $(SOURCE_ACTIVATE) $(PIP) install --default-timeout=100 -r requirements.development.txt 2>&1 | grep Downloading
	@ $(SOURCE_ACTIVATE) $(PYTHON) setup.py install
	@ touch bin/activate

deploy: bin/activate
	@ echo "[ deployed     ] the system was completly deployed"

show-version:
	@ $(SOURCE_ACTIVATE) $(PYTHON) --version

test:
	@ $(SOURCE_ACTIVATE) $(PYTHON) tests/netcdf_test.py
	@ echo "[ tested       ] the system was completly tested"

test-coverage-travis-ci:
	@ $(SOURCE_ACTIVATE) coverage run tests/netcdf_test.py

test-coveralls:
	@ $(SOURCE_ACTIVATE) coveralls

test-coverage: test-coverage-travis-ci test-coveralls

pypi-upload: test
	@ echo "[ uploading    ] package to pypi servers"
	@ ($(SOURCE_ACTIVATE) $(PYTHON) setup.py sdist upload 2>&1) >> tracking.log
	@ echo "[ uploaded     ] the new version was successfully uploaded"

clean:
	@ echo "[ cleaning     ] remove deployment generated files that doesn't exists in the git repository"
	@ sudo rm -rf virtualenv* hdf5* netcdf-4* bin/ lib/ lib64 include/ build/ share setuptools-*.tar.gz get-pip.py tracking.log subversion .Python
