"""

Haystack client.
Includes session and session management and basic get/put operations.
Supports basic authentication.

Adapted from pyox project at ox-framework.org

"""

import requests
#import logging

CONTENT_TYPE_HEADERS_DICT = {
    "json": {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        },
    "zinc": {
        'Content-Type': 'text/zinc',
        'Accept': 'text/zinc',
        },
    "csv": {
        'Content-Type': 'text/csv',
        'Accept': 'text/csv',
        },

    #"zinc":
}

class HSession(object):

    def __init__(self, url, username = None, password = None):
        """ Initialize instance, without establishing connection. Provide base URL """
        #  not been invoked yet
        # base URL
        self.url = url
        self.headers = {}
        self.contentTypeHeaders = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            #'Accept-Encoding': 'gzip, deflate',
        }
        self._contentType = 'zinc'

        self.session = requests.Session()
        # will contains the last response received
        self.response = None
        if username:
            self.session.auth = (username, password)

    @property
    def contentType(self):
        return self._contentType

    @contentType.setter
    def contentType(self, value):
        headers = CONTENT_TYPE_HEADERS_DICT.get(value)
        if not headers:
            raise ValueError("ContentType not supported: %s" % value)
        self._contentType = value
        self.contentTypeHeaders = headers

    def addHeader(self, name, value):
        """ Adds header that will be used for requests """
        self.headers[name] = value

    def post(self, url, body):
        """ Perform a POST request.
        TODO: fully implement and test this
        """
        #import pdb
        #pdb.set_trace()
        
        return self.doUrlRequest(url, body, 'POST')

    def get(self, url):
        """ Perform a GET request"""
        return self.doUrlRequest(url)

    def put(self, url, body):
        """ Perform a PUT request using href with a body as target of PUT.
        TODO: fully implement and test this
        """
        #url = obj.href
        #body = obj.toXML()
        return self.doUrlRequest(url, body, 'PUT')

    #def __str__(self):
    #    logging.info('Session: %s' % self.url)

    #************** Private functions **************

    def doUrlRequest(self, url, body = None, method = 'GET'):
        """Perform url request.
        Args:
            url: url to request
            in: HTTP POST body (needed only for POST requests)
            method: HTTP method to use
        """

        #request.add_header('Connection', 'keep-alive')
        #request.add_header('Content-Length', len(input))
        currentHeaders = self.contentTypeHeaders
        #print("url=%s" % url)
        # merge with header set by user
        currentHeaders.update(self.headers)
        try:
            if method == 'GET':
                res = self.session.get(url, headers=currentHeaders)
            elif method == 'POST':
                res = self.session.post(url, data=body, headers=currentHeaders)
            else:
                raise ValueError("Method %s is not supported right now." % method)
            
            self.response = res.status_code
            res.encoding = "utf-8"
            content = res.text 
        except Exception, err:
            raise Exception("Can't perform request to %s: %s" % (url, err))
        #except httplib.BadStatusLine, err:
        #    raise Exception("BadStatusLine for %s: %s" % (url, err))
        #except httplib2.RedirectLimit, err:
        #    self.response = err.response
        #    content = err.content

        return content

