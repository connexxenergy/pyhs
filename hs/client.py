"""

Haystack client.
Includes session and session management and basic get/put operations.


"""

import json
#import logging
from hs.val import HStr
from session import HSession
from core import Storage
from io import ZincReader, ZincWriter
from grid import HGridBuilder
class HClient(object):
    """ Haystack client.
    
    This client uses json payload.
    
    Examples:
        >>> from hs.client import HClient
        >>> client = HClient("http://localhost:1225/haystack")
        >>> client.about()
        >>> client.readAll("point")
        >>> client.hisRead("@D-AHU1-DTemp", "yesterday")

        >>> import hs.client
        >>> client = hs.client.HClient("http://localhost:1225/haystack")
        >>> client.about()
        >>> client.readById("@11-CurrentTemperature")

        
    """
    def __init__(self, url, username = None, password = None):
        self.session = HSession(url, username, password)
        self.url = url

    @property
    def contentType(self):
        return self.session.contentType

    @contentType.setter
    def contentType(self, value):
        self.session.contentType = value

    def _parseResponse(self, res):
        if self.contentType == "json":
            ret = Storage(json.loads(res))
        elif self.contentType == "csv":
            #ret = res.decode("utf-8")
            ret = res
        else:
            ret = ZincReader(res).readGrid()
        return ret

    def about(self):
        """Perform about operation.
        """
        res = self.session.get("%s/about" % self.url)
        return self._parseResponse(res)

    def ops(self):
        """Perform ops operation.
        """
        res = self.session.get("%s/ops" % self.url)
        return self._parseResponse(res)

    def formats(self):
        """Perform formats operation.
        """
        res = self.session.get("%s/formats" % self.url)
        return self._parseResponse(res)

    def readById(self, nid):
        """Read node by id.
        
        Args:
            nid: node id
        """

        res = self.session.get("%s/read?id=%s" % (self.url, nid))
        #print("readById: %s" % res)
        return self._parseResponse(res)
    
    def readAll(self, filt):
        """Read all points as given filter spec.
        Args:
            filt: filter
        """
        res = self.session.get("%s/read?filter=%s" % (self.url, filt))
        return self._parseResponse(res)

    #def read(self, filt):
    #    res = self.session.get("%s/read?filter=%s" % (self.url, filt))
    #    return Storage(json.loads(res))

    def hisRead(self, nid, hrange):
        """Read history for a given point.
        
        Args:
            nid: node id
            hrange: history range in haystack format
        """
        hrange = hrange.replace(' ', '%20')
        res = self.session.get('%s/hisRead?id=%s&range="%s"' % (self.url, nid, hrange))
        return self._parseResponse(res)

    def eval(self, expr):
        """Eval .

        Args:
            expr: eval expression
        """
        b = HGridBuilder()
        b.addCol("expr")
        b.addRow([HStr.make(expr)])
        grid = b.toGrid()
        data = ZincWriter.gridToString(grid)
        print("request to %s" % '%s/eval' % self.url)
        res = self.session.post('%s/eval' % self.url, data)
        print(res)
        return self._parseResponse(res)

    def nav(self, navId=None):
        """Perform nav command.
        Args:
            navId: navigation id (optional)
        """
        if navId:
            url = "%s/nav?navId=%s" % (self.url, navId)
        else:
            url = "%s/nav" % self.url
        res = self.session.get(url)
        return self._parseResponse(res)


