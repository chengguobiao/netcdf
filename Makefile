OS:=$(shell uname -s)
download = [ ! -f $(1) ] && echo "[ downloading  ] $(1)" && curl -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.149 Safari/537.36" -O $(2)/$(1) || echo "[ downloaded   ] $(1)"
unpack = [ ! -d $(2) ] && echo "[ unpacking    ] $(1)" && tar xzf $(1) || echo "[ unpacked     ] $(1)"

define get
	@ $(call download,$(2),$(3))
	@ $(call unpack,$(2),$(1))
endef

define compile
	@ cd $(1) && \
	([ -f ./configure ] && echo "[ configuring  ] $(1)" && ($(2) sh ./configure $(3) 2>&1) >> ../tracking.log || echo "[ configured   ] $(1)") && \
	echo "[ compiling    ] $(1) with $(NPROC) cores" && \
	(make -j $(NPROC) 2>&1) >> ../tracking.log && \
	echo "[ installing   ] $(1)" && \
	(sudo make $(4) 2>&1) >> ../tracking.log
endef

define install
	@ $(call get,$(1),$(2),$(3))
	@ $(call compile,$(1),,,install)
endef

update_shared_libs=sudo ldconfig
ifeq ($(OS), Darwin)
	NPROC=$(shell sysctl -n hw.ncpu)
	update_shared_libs=
	LIBHDF5=/usr/local/lib/libhdf5_hl.8.dylib
	LIBNETCDF=/usr/local/lib/libnetcdf.7.dylib
endif
ifeq ($(OS), Linux)
	NPROC=$(shell nproc)
	LIBHDF5=/usr/local/lib/libhdf5.so.8.0.1
	LIBNETCDF=/usr/local/lib/libnetcdf.so.7.2.0
endif

PYPREFIX_PATH=/usr
PYTHONLIBS=LD_LIBRARY_PATH=/usr/lib
PYTHONPATH=$(PYPREFIX_PATH)/bin/python  
FIRST_EASYINSTALL=$(PYTHONLIBS) easy_install
PIP=bin/pip
PYTHON=bin/python
EASYINSTALL=bin/easy_install
VIRTUALENV=virtualenv
SOURCE_ACTIVATE=$(PYTHONLIBS) . bin/activate; 
HDF5VER=1.8.12

unattended:
	@ (sudo ls 2>&1) >> tracking.log

ubuntu:
	@ (sudo apt-get -y install zlibc curl libssl0.9.8 libbz2-dev libxslt*-dev libxml*-dev 2>&1) >> tracking.log
	@ echo "[ assume       ] ubuntu distribution"

$(LIBHDF5):
	$(call get,hdf5-$(HDF5VER),hdf5-$(HDF5VER).tar.gz,http://www.hdfgroup.org/ftp/HDF5/releases/hdf5-$(HDF5VER)/src)
	$(call compile,hdf5-$(HDF5VER),,--prefix=/usr/local --enable-shared --enable-hl,install)

$(LIBNETCDF): $(LIBHDF5)
	$(call get,netcdf-4.3.1-rc4,netcdf-4.3.1-rc4.tar.gz,ftp://ftp.unidata.ucar.edu/pub/netcdf)
	$(call compile,netcdf-4.3.1-rc4,LDFLAGS=-L/usr/local/lib CPPFLAGS=-I/usr/local/include,--enable-netcdf-4 --enable-dap --enable-shared --prefix=/usr/local,install)

libs-and-headers: $(LIBNETCDF)
	@ $(update_shared_libs)

deployment: libs-and-headers
	@ echo "[ installing   ] $(PIP) requirements for deployment"
	@ sudo pip install --default-timeout=100 -r requirements.deployment.txt 2>&1

bin/activate: requirements.txt
	@ echo "[ using        ] $(PYTHONPATH)"
	@ echo "[ installing   ] $(VIRTUALENV)"
	@ (sudo $(FIRST_EASYINSTALL) virtualenv 2>&1) >> tracking.log
	@ echo "[ creating     ] $(VIRTUALENV) with no site packages"
	@ ($(PYTHONLIBS) $(VIRTUALENV) --python=$(PYTHONPATH) --no-site-packages . 2>&1) >> tracking.log
	@ echo "[ installing   ] $(PIP) inside $(VIRTUALENV)"
	@ ($(SOURCE_ACTIVATE) $(EASYINSTALL) pip 2>&1) >> tracking.log
	@ echo "[ installing   ] numpy inside $(VIRTUALENV)"
	@ ($(SOURCE_ACTIVATE) $(EASYINSTALL) numpy 2>&1) >> tracking.log
	@ echo "[ installing   ] $(PIP) requirements"
	@ $(SOURCE_ACTIVATE) $(PIP) install --default-timeout=100 -r requirements.deployment.txt 2>&1 | grep Downloading
	@ $(SOURCE_ACTIVATE) $(PIP) install --default-timeout=100 -r requirements.development.txt 2>&1 | grep Downloading
	@ $(SOURCE_ACTIVATE) $(PIP) install --default-timeout=100 -r requirements.txt 2>&1 | grep Downloading
	@ touch bin/activate

deploy: libs-and-headers bin/activate
	@ echo "[ deployed     ] the system was completly deployed"

show-version:
	@ $(SOURCE_ACTIVATE) $(PYTHON) --version

test:
	@ $(SOURCE_ACTIVATE) $(PYTHON) netcdf/test_netcdf.py
	@ echo "[ tested       ] the system was completly tested"

test-coverage-travis-ci:
	@ $(SOURCE_ACTIVATE) coverage run --source='netcdf/' netcdf/test_netcdf.py

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

hardclean: clean
	@ echo "[ cleaning     ] remove manually installed libraries"
	@ sudo rm -rf $(LIBHDF5) $(LIBNETCDF)
