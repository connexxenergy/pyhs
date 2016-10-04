""" Haystack Grid and related classes.


This includes the implemetatio of row, col, dict, grid and related classes and functions.


"""
import copy
import sys
import traceback
from val import *

# tag characters validation table
TAG_CHARS = [False] * 128

def init_tag_chars():
    """Initialize static validation table"""
    for i in range(ord('a'), ord('z')+1):
        TAG_CHARS[i] = True
    for i in range(ord('A'), ord('Z')+1):
        TAG_CHARS[i] = True
    for i in range(ord('0'), ord('9')+1):
        TAG_CHARS[i] = True
    TAG_CHARS[ord('_')] = True


init_tag_chars()

def istagname(n):
    """
     Returns True if the given string is a legal tag name.  The
     first char must be ASCII lower case letter.  Rest of
     chars must be ASCII letter, digit, or underbar.
    """
    if not len(n): return False
    first = ord(n[0])
    if first < ord('a') or first > ord('z'): return False
    for c in n:
        if ord(c) >= 128 or not TAG_CHARS[ord(c)]:
            return False
    return True




class HCol(object):
    """HCol is a column in a HGrid.
        @see {@link http://project-haystack.org/doc/Grids|Project Haystack}
    """
    def __init__(self, index, name, meta):
        self.index = index
        self.name = name                  
        self._meta = meta

    @property
    def meta(self):
        return self._meta

    @property
    def dis(self):
        """Return display name of column which is dict.dis or name"""                  
        dis = self._meta.get("dis")
        if isinstance(dis, HStr):
            return dis.val
        else:
            return self.name
            
    def __eq__(self, other):
        return isinstance(other, HCol) and self.name == other.name and self._meta == other._meta


class HDictBuilder(dict):
    """HDictBuilder is used to construct an immutable HDict instance.
        @see {@link http://project-haystack.org/doc/TagModel#tags|Project Haystack}

    """
    #def __init__(self):
    #    pass
        
    def is_empty(self):
        return len(self)
        
    def has(self, name):
        return self.get(name) != None

    def missing(self, name):
        return self.get(name) == None

    @property
    def dis(self):
        """Get display string for this entity:
            - dis tag
            - id tag

        """
        ret = "????"
        v = self.get('dis')
        if isinstance(v, HStr):
            ret = v.val
        else:
            v = self.get('id')
            if v != None:
                ret = v.dis()
        return ret

    def add(self, name, val = None, unit = None):
        """Add name/value/unit to the instance.
        :param name:
        :param val:
        :param unit:
        :return: self
        """
        """
        :param name:
        :param val:
        :param unit:
        :return:
        """
        # print('add: %s' % name)
        if not istagname(name):
            raise ValueError("Invalid tag name: %s" % name)
        if val == None:
            self[name] = HMarker.VAL
        else:
            if isinstance(val, basestring):
                self[name] = HStr(val)
            elif isinstance(val, int) or isinstance(val, float) or isinstance(val, long):
                self[name] = HNum(val, unit)
            elif issubclass(type(val), HVal):
                self[name] = val
            else:
                raise ValueError("value type not supported: %s" % type(val))
                #self[name] = val
        return self

    def add_dict(self, hdict):
        """Add all items from an hdict.
        """
        for name, value in hdict.iteritems():
            self.add(name, value)
        return self

    """
    def getbool(self, name):
        pass
        
    def getstr(self, name):
        pass
        
    def getref(self, name):
        pass
        
    def getint(self, name):
        pass
        
    def getdouble(self, name):
        pass
    """
    def toDict(self):
        """Convert current state to an immutable HDict instance.
        Clear current state of builder (empty it). 
        """
        if not len(self):
            return HDict.EMPTY
        ret = HDict(copy.copy(dict(self)))
        self.clear()
        return ret
    
        
"""

"""
    
    
    
class HDict(dict):
    """HDict is an immutable map of name/HVal pairs.  Use HDictBuilder
      to construct a HDict instance.
      @see {@link http://project-haystack.org/doc/TagModel#tags|Project Haystack}

    """
    #def __init__(self):
    #    pass
    def __setitem__(self, key, value):
        raise Exception("Can't modify the immutable HDict instance")
        
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    @property
    def dis(self):
        v = self.get("dis")
        if isinstance(v, HStr):
            return v.val
        v = self.get("id")
        if v != None:
            return v.dis
        else:
            return "????"



    # equal operator will work automatically since dict operator will be invoked 
    # and do the right thing
    #def __eq__(self, other):
    #        pass

    def is_empty(self):
        return len(self) == 0

    def has(self, name):
        return self.get(name) != None

    def missing(self, name):
        return self.get(name) == None

    def id(self):
        return self.getRef("id")

    def __str__(self):
        return self.to_zinc()

    def to_zinc(self):
        s = StringIO.StringIO()
        first = True
        for name, value in self:
            #print "to_zinc: %s, %s" % (name, value)
            if first:
                first = False
            else:
                s.write(' ')
            s.write(name)
            if not value == HMarker.VAL:
                s.write(':')
                s.write(value.to_zinc())
        return s.getvalue()


class HRow(HDict):
    """HRow is a row in a HGrid.  It  also implements the HDict "interface".
        @see <a href='http://project-haystack.org/doc/Grids'>Project Haystack</a>
    """
    def __init__(self, grid, cells):
        self.grid = grid
        self.cells = cells
        # populate name, value pairs into the internal dict so that
        #  HDict "interface" works properly
        for i, col in enumerate(grid.cols):
            self[col.name] = cells[i]

    def __setitem__(self, key, value):
        """Override setitme to avoid HDict exception when
        invoking ctor:
        raise Exception("Can't modify the immutable HDict instance")
        """
        dict.__setitem__(self, key, value)


    def size(self):
        return len(self.grid.cols)

    def get(self, col):
        """Get a cell by column.

        Note: not implemented check used in Java API: If cell is null then raise
            Error or return  None based on checked flag.

        """
        ret = None
        if isinstance(col, HCol):
            ret = self.cells[col.index]
        else:
            name = col
            col = self.grid.col(name)
            if col:
                ret = self.cells[col.index]
        return ret


    def __iter__(self):
        """
        Return name/value iterator which only includes non-null cells
        """
        return HRowIterator(self.cells)


class HRowIterator(object):
    """Iterator which only includes non-null cells.
    Similar to Java prototype, but returns value not entry (key,val) pair
    """

    def __init__(self, cells):
        self.current = 0
        self.cells = cells

    def __iter__(self):
        return self

    def next(self):
        #print("HGridIterator: %s" % self.rows)
        if self.current >= len(self.cells):
            raise StopIteration
        else:
            #print self.cells[self.current]
            # skip null cells
            while self.current < len(self.cells) and self.cells[self.current] == None:
                #print self.cells[self.current]
                self.current += 1
            #print "Returning", self.cells[self.current]
            if self.current >= len(self.cells):
                raise StopIteration
            self.current += 1
            return self.cells[self.current-1]




class HGrid():
    """HGrid is an immutable two dimension data structure of cols and rows.
        Use HGridBuilder to construct a HGrid instance.
        @see {@link http://project-haystack.org/doc/Grids|Project Haystack}

    
    """
    def __init__(self, meta, cols, rows):
        self.meta = meta
        self.cols = cols
        
        self.rows = []
        for cells in rows:
            if len(cells) != len(cols):
                raise ValueError("Row cells size != cols size")
            self.rows.append(HRow(self, cells))
            
        self.cols_dict = {}
        for col in cols:
            name = col.name
            if self.cols_dict.get(name):
                ValueError("Duplicate col name: " + name)
            self.cols_dict[name] = col

    def is_err(self):
        return self.meta.has("err")

    def is_empty(self):
        return not self.num_rows()

    def num_rows(self):
        return len(self.rows)

    def row(self, index):
        return self.rows[index]

    def num_cols(self):
        return len(self.cols)

    def col(self, index):
        if isinstance(index, basestring):
            return self.cols_dict.get(index)
        elif isinstance(index, int):
            return self.cols[index]
        else:
            raise ValueError("index of incorrect type: %s" % index)

    def __iter__(self):
        return HGridIterator(self.rows)


class HGridIterator(object):

    def __init__(self, rows):
        self.current = 0
        self.rows = rows

    def __iter__(self):
        return self

    def next(self):
        #print("HGridIterator: %s" % self.rows)
        if self.current >= len(self.rows):
            raise StopIteration
        else:
            self.current += 1
            return self.rows[self.current-1]




class BCol():
    """Helper class for HGridBuilder.
    """
    def __init__(self, name):
        self.name = name 
        self.meta = HDictBuilder()
    
class HGridBuilder():
    """HGridBuilder is used to construct an immutable HGrid instance.
    @see <a href='http://project-haystack.org/doc/Grids'>Project Haystack</a>
    """
    def __init__(self):
        """constructor
        """
        self.meta = HDictBuilder()
        self.cols = []
        self.rows = []

    def dictToGrid(self, hdict):
        b = HGridBuilder()
        cells = []
        for name, value in hdict.iteritems():
            b.addCol(name)
            cells.append(value)
        b.rows.append(cells)
        return b.toGrid()

    def dictsToGrid(self, meta, dicts):
        """Convenience to build grid from array of HDict.
         * Any null entry will be row of all null cells.
         * @return {HGrid}
        """
        if not len(dicts):
            ret = HGrid(meta, 
                [HCol(0, "empty", HDict.EMPTY)],
                [])
        else:
            b = HGridBuilder()
            b.meta.add_dict(meta)

            # collect column names
            cols = []
            for d in dicts:
                for n,v in d.items():
                    if not n in cols: 
                        cols.append(n)
                        b.addCol(n)
            if not len(cols):
                cols.append("empty")
                b.addCol("empty")                    
            # now map rows
            colsize = len(b.cols)
            for d in dicts:
                cells = []
                for i in range(colsize):
                    if d == None:
                        cells.append(None)
                    else:
                        cells.append(d.get(b.cols[i].name))
                b.rows.append(cells)
            ret = b.toGrid()
        return ret


    def errToGrid(self, e, meta_dis=None):
        """Create grip for error.
        Args:
            e: error to be used for grid
            meta_dis: if specified, used as meta "dis" field

        """
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #trace = repr(traceback.extract_tb(exc_traceback))
        trace = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
        b = HGridBuilder()
        if meta_dis is None:
            meta_dis = e
        b.meta.add("err").\
            add("dis", "%s" % meta_dis).\
            add("errTrace", trace)
        b.addCol("empty")
        return b.toGrid()

    def hisItemsToGrid(self, meta, items, tzname=None):
        """Convenience to build grid from a list of HHisItem .
        Args:
            meta: meta to use for grid
            items: list of items as ts, val pair
        """      
        b = HGridBuilder()
        b.meta.add_dict(meta)
        b.addCol("ts")
        b.addCol("val")
        for ts, val in items:
            hts = HDateTime.make_from_dt(ts, tzname)
            if isinstance(val, basestring):
                hval = HStr.make(val)
            elif isinstance(val, int) or isinstance(val, float) or isinstance(val, long):
                hval = HNum.make(val)
            elif isinstance(val, bool):
                hval = HBool.make(val)
            elif issubclass(type(val), HVal):
                hval = val
            else:
                raise ValueError("value type not supported: %s" % type(val))
            b.addRow([hts, hval])
        return b.toGrid()
                     
    def addCol(self, name):
        """Add new column and return builder for column metadata.
           Columns cannot be added after adding the first row.
        """
        if len(self.rows):
            raise ValueError("Cannot add cols after rows have been added")
        if not istagname(name):
            raise ValueError("Invalid column name: " + name)
        col = BCol(name)
        self.cols.append(col)
        return col.meta
        
    def addRow(self, cells):
        """
        Add new row with list of cells which correspond to column
        order.  
        Returns: self
        
        """
        if len(self.cols) != len(cells):
            raise ValueError("Row cells size != cols size")
        # append a cloned list
        self.rows.append(list(cells))
        return self

    def toGrid(self):
        """Convert current state to an immutable HGrid instance .
        """
        meta = self.meta.toDict()
        cols = []
        for i in range(len(self.cols)):
            col = self.cols[i]
            cols.append(HCol(i, col.name, col.meta.toDict()))
        return HGrid(meta, cols, self.rows)

"""

"""    
        

HDict.EMPTY = HDict({})
        
# Empty grid with one column called "empty" and zero rows
HGrid.EMPTY = HGrid(HDict.EMPTY, [HCol(0, "empty", HDict.EMPTY)], [])


