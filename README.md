# pyhs: Python Haystack Client Library

Also see: http://project-haystack.org

## Scope 

Currently pyhs supports parsing and encoding zinc, and encoding JSON and CSV.
Parsing of JSON or CSV is currently not supported.

In addition to standard haystack zinc encoding/decoding, pyhs also supports the following extensions:

* multi-grid payload encoding and parsing/decoding (see test_zinc.py)

## Sample Usage

### Using Client in ZINC mode

Note: To execute this example, you need to specify valid URL and credential for a haystack server deployment.

    from hs.client import HClient
    from hs.io import ZincWriter
    from pprint import pprint
    client = HClient("http://cd.example.com/api/demo", "scott@example.com", "tiger")
    # note: default content type is "zinc" starting with pyhs version 3.0.
    #       default content type is "json" pyhs version 2.X.
    client.session.contentType = "zinc"
    zres = client.about()
    print(ZincWriter.gridToString(zres))
    ver:"2.0"
    vendorUri,tz,haystackVersion,serverTime,serverName,serverBootTime,productName,productVersion,productUri,vendorName
    `http://www.connexxenergy.com`,"UTC","2.0",2016-09-28T13:23:36.717Z UTC,"api.example-apps.com",2016-09-25T07:07:09.052Z UTC,"CX API Haystack Server (py)","0.2.19",`http://www.connexxenergy.com`,"Connexx Energy, Inc."

### Using Client in JSON mode

Note: the current implementation is using older encoding and has been tested with skyspark release prior to new
  JSON encoding implementation from http://project-haystack.org/forum/topic/258

Note: pprint is a standard Python library and used for pretty printing only

    from hs.client import HClient
    from pprint import pprint
    client = HClient("http://cd.example.com/api/demo", "scott@example.com", "tiger")
    # json is the default
    client.session.contentType = "json"
    client.about()
    res = client.about()
    pprint(res.as_dict())
    {u'cols': [{u'name': u'vendorUri'},
               {u'name': u'tz'},
               {u'name': u'haystackVersion'},
               {u'name': u'serverTime'},
               {u'name': u'serverName'},
               {u'name': u'serverBootTime'},
               {u'name': u'productName'},
               {u'name': u'productVersion'},
               {u'name': u'productUri'},
               {u'name': u'vendorName'}],
     u'meta': {u'ver:': u'2.0'},
     u'rows': [{u'haystackVersion': u'2.0',
                u'productName': u'CX API Haystack Server (py)',
                u'productUri': u'http://www.connexxenergy.com',
                u'productVersion': u'0.2.10',
                u'serverBootTime': u'2016-03-25T11:37:42.178Z UTC',
                u'serverName': u'api.example-apps.com',
                u'serverTime': u'2016-03-25T15:52:35.686Z UTC',
                u'tz': u'UTC',
                u'vendorName': u'Connexx Energy, Inc.',
                u'vendorUri': u'http://www.connexxenergy.com'}]}



## Pre-requisites:

Python  2.7.x or installed on the system (on unix usually installed by default).

The libraries as specified in requirements.txt need to be installed, e.g. via "pip install" on Linux or OSX:

    pip install -r requirements.txt

If you want to generate documentation, epydoc has to be installed:

    sudo pip install epydoc

## To Build and Install

To install within your python installation run the following from your
command prompt:

On linux:

	sudo python setup.py install

On windows:

	python setup.py install

## Running Unit Tests

* Prerequisites:

See requirements-test.txt for test requirements (need nose library)

    sudo pip install -r requirements-test.txt

For client tests to pass, url/username/password have to be configured and point
to a haystack repository similar to skyspark's "demo" project.

* Run:

    nosetests test/*.py

* Sample output:

    ............
    ----------------------------------------------------------------------
    Ran 12 tests in 0.010s
    
    OK


## To build the deployment tar file from sources:


Update version:

	vi ./hs/__init__.py VERSION

Clean and build:

    ./package.sh

The result of packagng will look like this:

    ...
    The archives have been built in build directory:
    pyhs-0.3.0		pyhs-0.3.0.tar.gz	pyhs-0.3.0.zip


To generate and deploy docs to the doc directory:

    mkdir -p build/doc/api ; epydoc hs --name 'pyhs library' --graph all  -o build/doc/api
    # view docs
    open build/doc/api/index.html
	# deploy to a remote server:
    scp -r build/doc/api/* server:/path/to/api/pyox

Note: to generate graphs, graphviz has to be installed. This is now to install it on Mac/Yosemite:

    brew install gts librsvg freetype
    brew install graphviz --with-bindings --with-freetype --with-librsvg --with-pangocairo
    pip install graphviz

## OS Support

This has been tested on Mac OSX and Linux/Ubuntu. Windows has not been tested.
Build scripts are written in bash and should run under cygwin on windows.


## TODO

The following features and fixes need to be added to bring pyhs on par with Brian Frank's Java Haystack implementation:

* make Bool literals work (test_filter.testParseZincLiterals)
* Upgrade JSONWriter to support new JSON encoding as per http://project-haystack.org/forum/topic/258
* add JSON parsing (JSONReader) (JSONWriter is already implemented)
* add CSV parsing (CSVReader) (CSVWriter is already implemented)

Also, the following additional feature should be implemented:

* hisWrite extension that support multi-point write
* "create new record" extension
* write more unit tests (similar coverage to Java Haystack)

