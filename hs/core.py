"""Core and utility classes and functions.

"""

class Storage(dict):
    """
    Based on web2py Storage class.
    A Storage object is like a dictionary except `obj.foo` can be used
    in addition to `obj['foo']`, and setting obj.foo = None deletes item foo.

        >>> o = Storage(a=1)
        >>> print o.a
        1

        >>> o['a']
        1

        >>> o.a = 2
        >>> print o['a']
        2

        >>> del o.a
        >>> print o.a
        None
    """
    __slots__ = ()
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __getitem__ = dict.get
    __getattr__ = dict.get
    __repr__ = lambda self: '<Storage %s>' % dict.__repr__(self)
    # http://stackoverflow.com/questions/5247250/why-does-pickle-getstate-accept-as-a-return-value-the-very-instance-it-requi
    __getstate__ = lambda self: None
    __copy__ = lambda self: Storage(self)
    
    def as_dict(self):
        """Return as dict instance"""
        ret = {}
        for key in self.keys():
            ret[key] = self[key]
        return ret


def parseHisItemNumberValues(hisItems, unit):
    """
    Parse history item numerical values.
    
    Do nothing if hisItem values are already numbers.
     
    
    This is useful if history returns Number type strings, such as:
    
    2014-01-01T00:00:01.975-05:00 New_York,0.0cfm
    2014-01-01T00:06:00.024-05:00 New_York,0.0cfm
    
    or
    
    2014-01-01T00:00:00.853-05:00 New_York,0.0%
    2014-01-01T00:06:00.008-05:00 New_York,0.0%

    Args:
        hisItems: list history items tuples to parse
        unit: unit which constitutes last part of hisItem values
        
    Return: 
        Parsed hisItems
    
    """
    if not hisItems:
        return hisItems
    if not isinstance(hisItems, list):
        raise ValueError("hisItems must be a list, but is %s" % type(hisItems))
    ts, val = hisItems[0]
    if isinstance(val, (int, long, float)):
        return hisItems
    if not isinstance(val, basestring):
        raise ValueError("hisItem value must be a string or number but is %s" % type(val))
        
    ret = []
    for ts,val in hisItems:
        index = val.find(unit)
        if index < 0:
            raise Exception("Number value %s doesn't contain unit %s" % (val, unit))
        val = val[:index]
        ret.append((ts, val))
    return ret

if __name__ == '__main__':
    import doctest
    doctest.testmod()
