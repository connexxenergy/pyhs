"""
Implementation of HVal classes.

"""
import math
import datetime
import StringIO
import dateutil.parser

############################################################
######################### Initialization ###################
############################################################

# initialize unit character table

UNIT_CHARS = [False] * 128


def init_unitchars():
    for i in range(ord('a'), ord('z')+1):
        UNIT_CHARS[i] = True
    for i in range(ord('A'), ord('Z')+1):
        UNIT_CHARS[i] = True
    for c in ['_', '$', '%', '/']:
        UNIT_CHARS[ord(c)] = True


# initialize haystack id character table

HSID_CHARS = [False] * 128

def init_hsidchars():
    """Initialize static validation table"""
    for i in range(ord('a'), ord('z')+1):
        HSID_CHARS[i] = True;
    for i in range(ord('A'), ord('Z')+1):
        HSID_CHARS[i] = True;
    for i in range(ord('0'), ord('9')+1):
        HSID_CHARS[i] = True;
    for c in ['_', ':', '-', '.', '~']:
        HSID_CHARS[ord(c)] = True;

init_unitchars()
init_hsidchars()

############################################################
################### Internal Helper Functions ##############
############################################################

def _is_unit_name(unit):
    if unit == None:
        ret = True
    elif not len(unit):
        ret = False
    else:
        for i in range(len(unit)):
            c = ord(unit[i])
            if c < 128 and c > 0 and UNIT_CHARS[c]:
                ret = True
            else:
                ret = False
    return ret

def _is_id(hsid):
    """Return True if the given string is a valid id for a reference.
    """
    if not len(hsid): return False
    for c in hsid:
        cc = ord(c)
        if cc < 0 or cc >= len(HSID_CHARS) or not HSID_CHARS[cc]:
            return False
    return True

def is_id_char(c):
    """Return True if the given character is a valid id for a reference.
    """
    if c == "":
        return False
    cc = ord(c)
    return cc >= 0 and cc < len(HSID_CHARS) and HSID_CHARS[cc]



############################################################
######################## Public Functions ##################
############################################################


def str_to_zinc(val = None):
    """Encode using double quotes and back slash escapes.
    Converts a string value to zinc, including
    handling of non-ascii chars.
    """
    s = StringIO.StringIO()
    s.write('"')
    for c in val:
        if c < " " or c == '"' or c == "\\":
            s.write("\\")
            if c == "\n":
                s.write("n")
            elif c == "\r":
                s.write("r")
            elif c == "\t":
                s.write("t")
            elif c == '"':
                s.write('"')
            elif c == "\\":
                s.write("\\")
            else:
                """
                corresponding java code:
                    s.append('u').append('0').append('0');
                    if (c <= 0xf) s.append('0');
                    s.append(Integer.toHexString(c));

                """
                s.write("u")
                s.write("0")
                s.write("0")
                if ord(c) < 0xf:
                    s.write("0")
                s.write(hex(ord(c)))
        else:
            s.write(c)
    s.write('"')
    return s.getvalue()


############################################################
########################### Classes ########################
############################################################



class HVal(object):
    """HVal implementation."""
    def __init__(self):
        """ctor"""

    def __str__(self):
        return self.to_zinc()

    def to_zinc(self):
        raise NotImplementedError("Must be implemented by subclass %s" % type(self))


    ## Comparison operators

    def __eq__(self, other):
        return type(self) == type(other) and str(self) == str(other)

    def __ne__(self, other):
        return type(self) != type(other) or str(self) != str(other)

    def __gt__(self, other):
        return type(self) == type(other) and str(self) > str(other)

    def __ge__(self, other):
        return type(self) == type(other) and str(self) >= str(other)

    def __lt__(self, other):
        return type(self) == type(other) and str(self) < str(other)

    def __le__(self, other):
        return type(self) == type(other) and str(self) <= str(other)

class HMarker(HVal):

    def __init__(self):
        pass

    def __eq__(self, other):
        return isinstance(other, HMarker) and self is other

    def __ne__(self, other):
        return not isinstance(other, HMarker) or self is not other

    def __str__(self):
        return "marker"

    def to_zinc(self):
        return "M"

HMarker.VAL = HMarker()
HMarker.JSON_VALUE = u"\u2713"

class HStr(HVal):
    """HStr wraps a str as a tag value."""
    def __init__(self, val):
        """ctor"""
        self.val = val

    @staticmethod
    def make(s):
        return HStr(s)

    def __str__(self):
        return self.val

    def to_zinc(self):
        return str_to_zinc(self.val)

    def to_code(self):
        """Encode using double quotes and back slash escapes.
        """
        return str_to_zinc(self.val)


class HBool(HVal):
    """HBool defines singletons for true/false tag values.
       @see <a href='http://project-haystack.org/doc/TagModel#tagKinds'>Project Haystack</a>
    """
    def __init__(self, val):
        """ctor"""
        self.val = val

    @staticmethod
    def make(v):
        return HBool(v)

    def to_zinc(self):
        return "T" if self.val else "F"

HBool.TRUE = HBool(True)
HBool.FALSE = HBool(False)


"""
  public static HDate make(int year, int month, int day)
  {
    if (year < 1900) throw new IllegalArgumentException("Invalid year");
    if (month < 1 || month > 12) throw new IllegalArgumentException("Invalid month");
    if (day < 1 || day > 31) throw new IllegalArgumentException("Invalid day");
    return new HDate(year, month, day);
  }
    """
class HDate(HVal):
    """HDate models a date (day in year) tag value."""
    
    def __init__(self, year, month, day):
        """ctor"""
        self.year = year
        self.month = month
        self.day = day

    @staticmethod
    def make(year, month, day):
        if year < 1900: raise ValueError("Invalid year")
        if month < 1 or month > 12: raise ValueError("Invalid month")
        if day < 1 or day > 31: raise ValueError("Invalid day")
        return HDate(year, month, day)

    @staticmethod
    def make_from_str(s):
        """Make date from string of the format yyyy-mm-dd.
        """
        dt = dateutil.parser.parse(s)
        return HDate(dt.year, dt.month, dt.day)

    @staticmethod
    def make_from_date(dt, tz=None):
        """Make instance from Python date.
        """
        return HDate(dt.year, dt.month, dt.day)

    def to_zinc(self, stream = None):
        ret = '%d-%02d-%02d' % ( self.year, self.month, self.day)
        if stream:
            stream.write(ret)
        return ret

    def __eq__(self, other):
        return type(self) == type(other) and \
               (self.year, self.month, self.day) == (other.year, other.month, other.day)

    def __ne__(self, other):
        return type(self) != type(other) or \
               (self.year, self.month, self.day) != (other.year, other.month, other.day)

    def __gt__(self, other):
        return type(self) == type(other) and \
               (self.year, self.month, self.day) > (other.year, other.month, other.day)

    def __ge__(self, other):
        return type(self) == type(other) and \
               (self.year, self.month, self.day) >= (other.year, other.month, other.day)

    def __lt__(self, other):
        return type(self) == type(other) and \
               (self.year, self.month, self.day) < (other.year, other.month, other.day)

    def __le__(self, other):
        return type(self) == type(other) and \
               (self.year, self.month, self.day) <= (other.year, other.month, other.day)




class HDateTime(HVal):
    """HDateTime models a timestamp with a specific timezone."""
    
    def __init__(self, date, time, tz, tz_offset = 0):
        self.date = date
        self.time = time
        self.tz = tz
        self.tz_offset = tz_offset

    @staticmethod
    def make(date, time, tz, tz_offset):
        if date == None or time == None or tz_offset == None:
            raise ValueError("null args")
        return HDateTime(date, time, tz, tz_offset)


    @staticmethod
    def make_from_dt(dt, tz=None):
        """Make instance from Python datetime.
        """
        if dt.tzinfo:
            tz_offset =  dt.tzinfo.utcoffset(dt).total_seconds()
        else:
            tz_offset = 0
        #tz_offset = 0
        date = HDate.make(dt.year, dt.month, dt.day)
        time = HTime.make(dt.hour, dt.minute, dt.second, dt.microsecond/1000)
        if not tz:
            tz = HTimeZone.DEFAULT
        return HDateTime(date, time, tz, tz_offset)

    @staticmethod
    def make_from_isostr(dt, tz=None):
        """Make instance from iso string.
        """
        dt = dateutil.parser.parse(dt)
        tz_offset = 0
        date = HDate.make(dt.year, dt.month, dt.day)
        time = HTime.make(dt.hour, dt.minute, dt.second, dt.microsecond/1000)
        if not tz:
            tz = HTimeZone.DEFAULT
        return HDateTime(date, time, tz, tz_offset)

    def __str__(self):
        return self.to_zinc()

    @staticmethod
    def now():
        return HDateTime.make_from_dt(datetime.datetime.utcnow())

    def to_zinc(self):
        s = StringIO.StringIO()
        self.date.to_zinc(s)
        s.write('T')
        self.time.to_zinc(s)
        if self.tz_offset == 0:
            s.write("Z")
        else:
            offset = self.tz_offset
            if offset < 0:
                s.write('-')
                offset = -offset
            else:
                s.write('+')
            zh = offset / 3600
            zm = (offset % 3600) / 60
            s.write('%02d:%02d' % (zh, zm))

        s.write(' %s' % self.tz)
        ret = s.getvalue()
        return ret


    def __eq__(self, other):
        return type(self) == type(other) and \
               (self.date, self.time, self.tz, self.tz_offset) == (other.date, other.time, other.tz, other.tz_offset)

    def __ne__(self, other):
        return type(self) != type(other) or \
               (self.date, self.time, self.tz, self.tz_offset) != (other.date, other.time, other.tz, other.tz_offset)

    def __gt__(self, other):
        return type(self) == type(other) and \
               (self.date, self.time, self.tz, self.tz_offset) > (other.date, other.time, other.tz, other.tz_offset)

    def __ge__(self, other):
        return type(self) == type(other) and \
               (self.date, self.time, self.tz, self.tz_offset) >= (other.date, other.time, other.tz, other.tz_offset)

    def __lt__(self, other):
        return type(self) == type(other) and \
               (self.date, self.time, self.tz, self.tz_offset) < (other.date, other.time, other.tz, other.tz_offset)

    def __le__(self, other):
        return type(self) == type(other) and \
               (self.date, self.time, self.tz, self.tz_offset) <= (other.date, other.time, other.tz, other.tz_offset)

class HTime(HVal):
    """HTime models a time of day tag value."""
    def __init__(self, hour, min, sec, ms = None):
        self.hour = hour
        self.min = min
        self.sec = sec if sec else 0
        self.ms = ms if ms else 0

    @staticmethod
    def make(hour, min, sec, ms = None):
        return HTime(hour, min, sec, ms)

    @staticmethod
    def make_from_str(s):
        dt = dateutil.parser.parse(s)
        return HTime(dt.hour, dt.minute, dt.second, dt.microsecond/1000)

    def to_zinc(self, stream = None):
        if not self.ms:
            ret = '%02d:%02d:%02d' % ( self.hour, self.min, self.sec)
        else:
            ret = '%02d:%02d:%02d.%03d' % ( self.hour, self.min, self.sec, self.ms)
        if stream:
            stream.write(ret)
        return ret

    def __eq__(self, other):
        return type(self) == type(other) and \
               (self.hour, self.min, self.sec, self.ms) == (other.hour, other.min, other.sec, other.ms)

    def __ne__(self, other):
        return type(self) != type(other) or \
               (self.hour, self.min, self.sec, self.ms) != (other.hour, other.min, other.sec, other.ms)

    def __gt__(self, other):
        return type(self) == type(other) and \
               (self.hour, self.min, self.sec, self.ms) > (other.hour, other.min, other.sec, other.ms)

    def __ge__(self, other):
        return type(self) == type(other) and \
               (self.hour, self.min, self.sec, self.ms) >= (other.hour, other.min, other.sec, other.ms)

    def __lt__(self, other):
        return type(self) == type(other) and \
               (self.hour, self.min, self.sec, self.ms) < (other.hour, other.min, other.sec, other.ms)

    def __le__(self, other):
        return type(self) == type(other) and \
               (self.hour, self.min, self.sec, self.ms) <= (other.hour, other.min, other.sec, other.ms)


class HTimeZone(HVal):
    def __init__(self, name):
        self.name = name
        #self.py_tz = py_tz

    @staticmethod
    def make(name):
        return HTimeZone(name)

    def __str__(self):
        return self.name;

    #def to_zinc(self, stream = None):


HTimeZone.UTC = HTimeZone.make("UTC")
HTimeZone.DEFAULT = HTimeZone.UTC

class HUri(HVal):
    """HUri models a URI as a string.
    @see <a href='http://project-haystack.org/doc/TagModel#tagKinds'>Project Haystack</a>
    """
    def __init__(self, val):
        self.val = val

    @staticmethod
    def make(val):
        #if not len(val):
        #    return HUri.EMPTY
        return HUri(val)

    def __str__(self):
        return self.val

    def to_zinc(self):
        return '`%s`' % self.val

HUri.EMPTY = HUri.make("")

class HNum(HVal):
    """HNum wraps a 64-bit floating point number and optional unit name."""
    
    def __init__(self, val, unit = None):
        if not _is_unit_name(unit):
            raise ValueError("Invalid unit name: " + unit)
        self.val = val
        self.unit = unit

    @staticmethod
    def make(val, unit = None):
        return HNum(val, unit)

    def to_zinc(self):
        # handle special values NaN/INF/-INF
        if math.isnan(self.val):
            s = "NaN"
        elif self.val == float("inf"):
            s = "INF"
        elif self.val == float("-inf"):
            s = "-INF"
        else:
            s = "%g" % self.val
        #s = '{0:g}'.format(self.val)
        if self.unit:
            s += " %s" % self.unit
        return s

    def __eq__(self, other):
        return type(self) == type(other) and (self is other or self.val == other.val)

    def __ne__(self, other):
        return type(self) != type(other) or self.val != other.val

    def __gt__(self, other):
        return type(self) == type(other) and self.val > other.val

    def __ge__(self, other):
        return type(self) == type(other) and self.val >= other.val

    def __lt__(self, other):
        return type(self) == type(other) and self.val < other.val

    def __le__(self, other):
        return type(self) == type(other) and self.val <= other.val

HNum.NaN = HNum(float('nan'))
HNum.POS_INF = HNum(float('inf'))
HNum.NEG_INF = HNum(float('-inf'))


"""
    StringBuffer s = new StringBuffer();
    if (val == Double.POSITIVE_INFINITY) s.append("INF");
    else if (val == Double.NEGATIVE_INFINITY) s.append("-INF");
    else if (Double.isNaN(val)) s.append("NaN");
    else
    {
      // don't let fractions
      double abs = val; if (abs < 0) abs = -abs;
      if (abs > 1.0)
        s.append(new DecimalFormat("#0.####", new DecimalFormatSymbols(Locale.ENGLISH)).format(val));
      else
        s.append(val);

      if (unit != null)
      {
        for (int i=0; i<unit.length(); ++i)
          s.append(unit.charAt(i));
      }
    }
    return s.toString();
"""
class HRef(HVal):
    """
    HRef wraps a string reference identifier and optional display name.
    @see <a href='http://project-haystack.org/doc/TagModel#tagKinds'>Project Haystack</a>
    """
    def __init__(self, val, dis):
        if not val or not _is_id(val): raise ValueError("Invalid id val: %s" % val);
        self.val = val
        self._dis = dis

    @staticmethod
    def make(val, dis = None):
        return HRef(val, dis)

    @property
    def dis(self):
        if self._dis != None: return self._dis
        else: return self.val

    def __str__(self):
        return self.val;

    #def __eq__(self, other):
    #    str(self) == str(other)

    def to_code(self):
        return '@%s' % self.val

    def to_zinc(self):
        s = '@%s' % self.val
        if self._dis != None:
            s += ' %s' % HStr(self._dis).to_zinc()
        return s




