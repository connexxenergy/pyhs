# coding: utf8
""" Implementation of zincreader and zincwriter
"""
import re
import json
import StringIO
import string
from grid import HGridBuilder, HDictBuilder
from val import HMarker, HBool, HStr, HNum, HDate, HRef, HTime, HTimeZone, HDateTime, HUri, is_id_char

class BaseWriter(object):
    pass

def _grid_to_string(grid, cls):
    """Write a grid to a string using the given writer type.

    :param grid:
    :param cls: class to use for conversion
    :return: string representaAon of grid
    """
    out = StringIO.StringIO()
    cls(out).writeGrid(grid)
    ret = out.getvalue()
    out.close()
    return ret

def _grids_to_string(grids, cls):
    """Write multigrid (haystack extension) grids to a string using the given writer type.

    :param grids:
    :param cls: class to use for conversion
    :return: string representaAon of grid
    """
    out = StringIO.StringIO()
    cls(out).writeGrids(grids)
    ret = out.getvalue()
    out.close()
    return ret

class CsvWriter(BaseWriter):
    """
   CsvWriter is used to write grids in comma separated values
   format as specified by RFC 4180.  Format details:
   <ul>
   <li>rows are delimited by a newline</li>
   <li>cells are separated by configured delimiter char (default is comma)</li>
   <li>cells containing the delimiter, '"' double quote, or
       newline are quoted; quotes are escaped as with two quotes</li>
   </ul>

   @see <a href='http://project-haystack.org/doc/Csv'>Project Haystack</a>

    haystack "multigrid" extension is supported which allows multiple grids in one
    payload - see writeGrids function.

    """
    def __init__(self, out, delimiter=','):
        """ctor
        Args:
            out: file stream, file or StringIO, to use for output
            Will write using utf-i

        """
        self.out = out
        self.delimiter = delimiter

    @staticmethod
    def gridToString(grid):
        return _grid_to_string(grid, CsvWriter)

    @staticmethod
    def gridsToString(grids):
        return _grids_to_string(grids, CsvWriter)

    def writeGrid(self, grid):
        """Write a grid to stream.

        Args:
            grid: grid to write

        """
        for i, col in enumerate(grid.cols):
            if i > 0:
                self.out.write(self.delimiter)
            self._writeCell(col.dis)
        self.out.write("\n")
        # rows
        for row in grid.rows:
            self._writeRow(grid, row)
            self.out.write("\n")

    def writeGrids(self, grids):
        """Write grids in extended haystack format (multigrid).

        CSV multigrids will be written with a new line separater, e.g. like this:

        header_label,header_value,type
        KPIs,RECENT,list

        value,label
        1000 KWH,KWH USED
        100 KW,KW PEAK
        $199.95,ENERGY CHARGE
        $199.95,ENERGY CHARGE


        :param grids:
        :return:
        """
        for i, grid in enumerate(grids):
            if i > 0:
                self.out.write('\n')
            self.writeGrid(grid)


    def _writeRow(self, grid, row):
        for i, col in enumerate(grid.cols):
            val = row.get(col)
            if i > 0:
                self.out.write(self.delimiter)
            self._writeCell(self._valToString(val))

    def _valToString(self, val):
        if val == None:
            return ""
        if val == HMarker.VAL:
            return HMarker.JSON_VALUE
        if isinstance(val, HRef):
            return val.to_zinc()
        return unicode(val)

    def _writeCell(self, cell):
        if not self.is_quoted_required(cell):
            self.out.write(unicode(cell))
        else:
            self.out.write('"')
            self.out.write(cell)
            self.out.write('"')

    def is_quoted_required(self, s):
        if not len(s):
            return True
        if s[0] in string.whitespace or s[-1] in string.whitespace:
            return True
        for c in s:
            if c == self.delimiter or c == '"' or c == '\n' or c == '\r':
                return True
        return False


class JsonWriter(object):

    """
    HJsonWriter is used to write grids in JavaScript Object Notation.
    It is a plain text format commonly used for serialization of data.
    It is specified in RFC 4627.

    @see <a href='http://project-haystack.org/doc/Json'>Project Haystack</a>

    haystack "multigrid" extension is supported which allows multiple grids in one
    payload - see writeGrids function.



    """
    def __init__(self, out):
        """ctor
        Args:
            out: file stream, file or StringIO, to use for output
            Will write using utf-i

        """
        self.out = out

    def writeGrid(self, grid):
        """Write a grid to stream.

        Args:
            grid: grid to write

        """
        json_dict = {}
        json_dict['meta'] = {
            "ver:": "2.0"
        }
        self._writeDictTags(grid.meta, json_dict['meta'])


        # columns
        cols = []
        for col in grid.cols:
            cols.append({"name":  col.name})
        json_dict["cols"] = cols

        # rows
        rows = []
        for row in grid.rows:
            json_row = {}
            self._writeDictTags(row, json_row)
            rows.append(json_row)

        json_dict["rows"] = rows
        self.out.write(json.dumps(json_dict))

    def writeGrids(self, grids):
        """Write grids in extended haystack format (multigrid).


        JSON multigrids will be written as a list of grids, like this:
        {
        "grids": [
            {
                "meta": {
                    "ver:": "2.0"
                },
                "cols": [
                {
            ...
            "rows": [
                {
            ...
            ]
            },
            {
                "meta": {
                    "ver:": "2.0"
                },
                ...
            },
        ]
        }


        :param grids:
        :return:
        """
        self.out.write('{"grids":[')
        for i, grid in enumerate(grids):
            if i > 0:
                self.out.write(',')
            self.writeGrid(grid)
        self.out.write(']}')

    @staticmethod
    def gridToString(grid):
        return _grid_to_string(grid, JsonWriter)

    @staticmethod
    def gridsToString(grids):
        return _grids_to_string(grids, JsonWriter)

    ############################################################
    ######################### Implementation ###################
    ############################################################

    def _writeDictTags(self, meta, meta_dict):
        for name, val in meta.iteritems():
            meta_dict[name] = unicode(val)


class ZincWriter(object):
    """HZincWriter is used to write grids in the Zinc format
        @see <a href='http://project-haystack.org/doc/Zinc'>Project Haystack</a>

    """
    def __init__(self, out):
        """ctor
        Args:
            out: file stream, file or StringIO, to use for output
            Will write using utf-i
        """
        self.out = out

    @staticmethod
    def gridToString(grid):
        return _grid_to_string(grid, ZincWriter)

    @staticmethod
    def gridsToString(grid):
        return _grids_to_string(grid, ZincWriter)

    def writeGrid(self, grid):
        self.out.write('ver:"2.0"')
        self._writeMeta(grid.meta)
        self.out.write('\n')

        # cols
        for i, col in enumerate(grid.cols):
            if i > 0:
                self.out.write(",")
            self._writeCol(col)

        self.out.write("\n")

        # rows
        for row in grid.rows:
            self._writeRow(grid, row)
            self.out.write("\n")

    def writeGrids(self, grids):
        """Write grids in extended haystack format (multigrid).
        :param grids:
        :return:
        """
        for grid in grids:
            self.writeGrid(grid)

    ############################################################
    ######################### Implementation ###################
    ############################################################

    def _writeMeta(self, meta):
        if meta.is_empty():
            return
        for name, val in meta.iteritems():
            self.out.write(' ')
            self.out.write(name)
            if (val != HMarker.VAL):
                self.out.write(':')
                self.out.write(val.to_zinc())

    def _writeCol(self, col):
        #print('_writeCol: %s: %s' % (col.name, col.meta))
        self.out.write(col.name)
        self._writeMeta(col.meta)

    def _writeRow(self, grid, row):
        for i, col in enumerate(grid.cols):
            val = row.get(col)
            #print('_writeRow: %s' % type(val))
            #print('_writeRow: %s' % val.to_zinc())
            if i > 0:
                self.out.write(',')
            if val == None:
                if i == 0:
                    self.out.write('N')
            else:
                self.out.write(val.to_zinc())

ZINC_GRID_START = 'ver:"2.0"'
class ZincReader(object):

    def __init__(self, s):
        """ctor

        Single grids (standard haystack) or
        multiple grids (extended haystack) are supported.

        Args:
            s: string to parse

        """
        if not isinstance(s, basestring):
            raise ValueError("Only basestring can be read via ZincReader")
        #
        # for multigrid, delineate individual grids
        #
        self.grid_strings = []
        start = 0
        curpos = 0

        # init strings for multiple grids
        str_boundaries = []
        for m in re.finditer(ZINC_GRID_START, s):
            str_boundaries.append(m.start())

        str_boundaries.append(len(s))


        if len(str_boundaries) < 2:
            # this is a dict, not a grid
            self.grid_strings.append(s)
        else:
            for i in range(len(str_boundaries)-1):
                self.grid_strings.append(s[str_boundaries[i]:str_boundaries[i+1]])


    def _init_grid_read(self, grid_number = 0):
        self.stream = StringIO.StringIO(self.grid_strings[grid_number])
        self.lineNum = 1
        self.version = None
        self.cur = chr(0)
        self.peek = chr(0)
        self.is_filter = False
        self._consume()
        self._consume()

    def readGrids(self):
        """Reads all grids from reader.

        Returns:
            list of HGrid instances

        """
        grids = []
        for i in range(len(self.grid_strings)):
            grids.append(self.readGrid(i))
        return grids

    def readGrid(self, grid_index=0):
        """Reads a single grid from reader.

        Args:
            grid_index: index of grid to read

        Returns:
            HGrid instance

        """
        self._init_grid_read(grid_index)
        b = HGridBuilder()

        # meta line
        self._readVer()
        self._readMeta(b.meta)
        self._consumeNewLine()

        # read cols
        numCols = 0
        while True:
            name = self._readId()
            self._skipSpace()
            numCols += 1
            self._readMeta(b.addCol(name))
            if self.cur != ",": break
            self._consume()
            self._skipSpace()

        self._consumeNewLine()

        # rows

        while self.cur != "\n" and self.cur != "":
            # preinit cells list to Nones
            cells = [None] * numCols
            for i in range(numCols):
                self._skipSpace()
                if self.cur != ',' and self.cur != '\n':
                    cells[i] = self._readVal()
                self._skipSpace()
                if (i+1 < numCols):
                    if self.cur != ',':
                        self._err("Expecting comma in row")
                    self._consume()
            self._consumeNewLine()
            b.addRow(cells)
        if self.cur == '\n': self._consumeNewLine()
        return b.toGrid()

    #def readGrids(self):
    #    acc = []
    #    while self.cur > 0:
    #        acc.append(self.readGrid())
    #    return acc

    def readDict(self):
        """ Read dict.
        Read dict from a previously instantiated single-grid reader.

        :return:
        """
        self._init_grid_read()
        b = HDictBuilder()
        self._readMeta(b)
        if self.cur != "":
            self._err("Expected end of stream")
        return b.toDict()

    def _readVer(self):
        id = self._readId()
        if not id == "ver":
            self._err("Expecting zinc header 'ver:2.0', not '%s'" % id)
        if self.cur != ':': self._err("Expecting ':' colon")
        self._consume()
        ver = self._readStrLiteral()
        if ver == "2.0":
            self.version = 2
        else:
            self._err("Expecting zinc version: %s" % ver)
        self._skipSpace()

    def _readMeta(self, b):
        """readMeta.
        Args:
            b: HDictBuilder
        """
        while isIdStart(self.cur):
            name = self._readId()
            val = HMarker.VAL
            self._skipSpace()
            if self.cur == ':':
                self._consume()
                self._skipSpace()
                val = self._readVal()
                self._skipSpace()
            b.add(name, val)
            self._skipSpace()

    def _readId(self):
        if not isIdStart(self.cur):
            self._err("Invalid name start char")
        s = StringIO.StringIO()
        while isId(self.cur):
            s.write(self.cur)
            self._consume()
        ret = s.getvalue()
        s.close()
        return ret



    ############################################################
    ############################ HVals #########################
    ############################################################

    def _readScalar(self):
        """Read scalar value."""
        val = self._readVal()
        if self.cur >= 0:
            self._err("Expected end of stream")

    def _readVal(self):
        """ Read a single scalar value from the stream."""
        if isDigit(self.cur):
            return self._readNumVal()
        if isAlpha(self.cur):
            return self._readWordVal()
        if self.cur == '@':
            return self._readRefVal()
        elif self.cur == '"':
            return self._readStrVal()
        elif self.cur == '`':
            return self._readUriVal()
        elif self.cur == '-':
            if self.peek == 'I':
                return self._readWordVal()
            else:
                return self._readNumVal()
        else:
            self._err("Unexpected char for start of value")

    def _readRefVal(self):
        self._consume()
        s = StringIO.StringIO()
        while is_id_char(self.cur):
            if self.cur == "":
                self._err("Unexpected end of ref literal")
            if self.cur == "\n" or self.cur == "\r":
                self._err("Unexpected newline of ref literal")
            s.write(self.cur)
            self._consume()
        self._skipSpace()
        dis = None
        if self.cur == '"':
            dis = self._readStrLiteral()
        return HRef.make(s.getvalue(), dis)


    def _readUriVal(self):
        s = StringIO.StringIO()
        # read string between backticks `...`
        self._consume()
        while self.cur != '`':
            s.write(self.cur)
            self._consume()
        self._consume()
        return HUri.make(s.getvalue())



    def _readWordVal(self):
        s = StringIO.StringIO()
        while True:
            s.write(self.cur)
            self._consume()
            try:
                if not isAlpha(self.cur) and not isSpecialUnit(self.cur):
                    break
            except Exception, e:
                self._err(e)


        word = s.getvalue()

        if self.is_filter:
            if word == "true":
                return HBool.TRUE
            if word == "false":
                return HBool.FALSE
        else:
            # this treats both of these None values properly as the same: ',N,' ',,'
            # 2012-04-21T08:45:00-04:00 New_York,N,76.3
            # 2012-04-21T08:45:00-04:00 New_York,,76.3
            if word == "N" or word == "":
                return None
            elif word == "M":
                return HMarker.VAL
            elif word == "R":
                return HStr.make("_remove_")
            elif word == "T":
                return HBool.TRUE
            elif word == "F":
                return HBool.FALSE
            elif word == "Bin":
                return self._readBinVal()
            elif word == "C":
                return self._readCoordVal()


        if word == "NaN":
            return HNum.NaN
        elif word == "INF":
            return HNum.POS_INF
        elif word == "-INF":
            return HNum.NEG_INF
        self._err("Unknown value identifier: %s" % word)


    def _readStrLiteral(self):
        self._consume()
        s = StringIO.StringIO()
        while self.cur != '"':
            if self.cur < 0:
                self._err("Unexpected end of str literal")
            if self.cur == '\n' or self.cur == '\r':
                self._err("Unexpected newline in str literal")
            if self.cur == '\\':
                s.write(self._readEscChar())
            else:
                s.write(self.cur)
                self._consume()
        self._consume()
        return s.getvalue()

    def _readStrVal(self):
        return HStr.make(self._readStrLiteral())

    def _readNumVal(self):
        # parse numeric part
        s = StringIO.StringIO()
        s.write(self.cur)
        self._consume()
        while isDigit(self.cur) or self.cur in [".", "_"]:
            if self.cur != '_':
                s.write(self.cur)
            self._consume()
            if self.cur in ['e', 'E']:
                if self.peek in ['-', '+'] or isDigit(self.peek):
                    s.write(self.cur)
                    self._consume()
                    s.write(self.cur)
                    self._consume()
        val = float(s.getvalue())

        #  HDate - check for dash
        date = None
        time = None
        hour = -1
        if self.cur == "-":
            try:
                year = int(s.getvalue())
            except Exception, ex:
                self._err("Invalid year for date value: %s" % s)
            self._consume()
            month = self._readTwoDigits("Invalid digit for month in date value: %s" % s)
            if self.cur != '-':
                self._err("Expected '-' for date value: %s" % s)
            self._consume()
            day = self._readTwoDigits("Invalid digit for day in date value: %s" % s)
            date = HDate.make(year, month, day)

            if self.cur != 'T':
                return date
            self._consume()
            hour = self._readTwoDigits("Invalid digit for hour in date time value")

        # HTime - check for colon
        if self.cur == ':':
            if hour < 0:
                if s.len != 2:
                    self._err("Hour must be two digits for time value: %s" % s)
                try:
                    hour = int(s.getvalue())
                except Exception, err:
                    self._err("Invalid hour for time value: %s" % s)
            self._consume()
            min = self._readTwoDigits("Invalid digit for minute in time value")
            if self.cur != ':':
                self._err("Expected ':' for time value")
            self._consume()
            sec =     self._readTwoDigits("Invalid digit for seconds in time value")
            ms = 0
            if self.cur == '.':
                self._consume()
                places = 0
                while isDigit(self.cur):
                    ms = (ms*10) + (ord(self.cur) - ord('0'))
                    self._consume()
                    places += 1
                if places == 1:
                    ms *= 100
                elif places == 2:
                    ms *= 10
                elif places == 3:
                    pass
                else:
                    self._err("Too many digits for milliseconds in time value")

            time = HTime.make(hour, min, sec, ms)
            if date == None:
                return time

        zutc = False
        if date != None:
            tz_offset = 0
            if self.cur == 'Z':
                self._consume()
                zutc = True
            else:
                neg = self.cur == '-'
                if self.cur != '-' and self.cur != '+':
                    self._err("Expected -/+ for timezone offset")
                self._consume()
                tz_hours = self._readTwoDigits("Invalid digit for timezone offset")
                if self.cur != ':':
                    self._err("Expected colon for timezone offset")
                self._consume()
                tz_mins = self._readTwoDigits("Invalid digit for timezone offset")
                tz_offset = tz_hours * 3600 + tz_mins * 60
                if neg:
                    tz_offset = -tz_offset

            # timezone name
            if self.cur != ' ':
                if not zutc:
                    self._err("Expected space between timezone offset and name")
                else:
                    tz = HTimeZone.UTC
            elif zutc and not (self.peek >= 'A' and self.peek <= 'Z' ):
                tz = HTimeZone.UTC
            else:
                self._consume()
                if not isTz(self.cur):
                    self._err("Expected timezone name")
                s = StringIO.StringIO()
                while isTz(self.cur):
                    s.write(self.cur)
                    self._consume()
                tz = HTimeZone.make(s.getvalue())
            return HDateTime.make(date, time, tz, tz_offset)

        # this was not validated as time or date, it is then HNum
        # if we have unit, parse that
        unit = None
        if isUnit(self.cur):
            s = StringIO.StringIO()
            while isUnit(self.cur):
                s.write(self.cur)
                self._consume()
            unit = s.getvalue()
        return HNum.make(val, unit);

    def _readTwoDigits(self, errMsg):
        if not isDigit(self.cur):
            self._err(errMsg)
        tens = (ord(self.cur) - ord('0')) * 10
        self._consume()
        if not isDigit(self.cur):
            self._err(errMsg)
        val = tens + (ord(self.cur) - ord('0'))
        self._consume()
        return val

    def _readEscChar(self):
        self._consume()
        if self.cur == 'b':
            self._consume()
            return '\b'
        elif self.cur == 'f':
            self._consume()
            return '\f'
        elif self.cur == 'n':
            self._consume()
            return '\n'
        elif self.cur == 'r':
            self._consume()
            return '\r'
        elif self.cur == 't':
            self._consume()
            return '\t'
        elif self.cur == '"':
            self._consume()
            return '"'
        elif self.cur == '$':
            self._consume()
            return '$'
        elif self.cur == '\\':
            self._consume()
            return '\\'

        if self.cur == 'u':
            self._consume()
            n3 = self._toNibble(self.cur)
            self._consume()
            n2 = self._toNibble(self.cur)
            self._consume()
            n1 = self._toNibble(self.cur)
            self._consume()
            n0 = self._toNibble(self.cur)
            self._consume()
            return n3 << 12 | n2 << 8 | n1 << 4 | n0
        self._err("Invalid hex char")

    def _consumeNewLine(self):
        if self.cur != "\n":
            self._err("Expecting newline")
        self._consume()

    def _consume(self):
        try:
            self.cur = self.peek
            self.peek = self.stream.read(1)
            if self.cur == '\n':
                self.lineNum += 1
        except Exception, e:
            self._err(e)


    def _consumeCmp(self):
        self._consume()
        if self.cur == '=':
            self._consume()
        self._skipSpace()

    def _skipSpace(self):
        while self.cur == ' ' or self.cur == '\t':
            self._consume()


    def _err(self, msg):
        s = "%s [Line %d]" % (msg, self.lineNum)
        s += "; follows: %s" % self.stream.getvalue()[self.stream.tell():]
        raise ValueError(s)

    def _toNibble(self, c):
        cc = ord(c)
        if c >= ord('0') and c <= ord('9'): return cc - ord('0')
        if c >= ord('a') and c <= ord('f'): return cc - ord('a') + 10
        if c >= ord('A') and c <= ord('Z'): return cc - ord('A') + 10
        self._err("Invalid hex char")

############################################################
######################### Char Types #######################
############################################################

def isDigit(c):
    if c == "":
        return False
    cc = ord(c)
    return cc > 0 and cc < 128 and (CHAR_TYPES[cc] & DIGIT) != 0

def isAlpha(c):
    if c == "":
        return False
    cc = ord(c)
    return cc > 0 and cc < 128 and (CHAR_TYPES[cc] & ALPHA) != 0

def isUnit(c):
    if c == "":
        return False
    cc = ord(c)
    return cc > 0 and cc < 128 and (CHAR_TYPES[cc] & UNIT) != 0

def isTz(c):
    if c == "":
        return False
    cc = ord(c)
    return cc > 0 and cc < 128 and (CHAR_TYPES[cc] & TZ) != 0

def isIdStart(c):
    if c == "":
        return False
    cc = ord(c)
    return cc > 0 and cc < 128 and (CHAR_TYPES[cc] & ID_START) != 0

def isId(c):
    if c == "":
        return False
    cc = ord(c)
    return cc > 0 and cc < 128 and (CHAR_TYPES[cc] & ID) != 0

def isSpecialUnit(c):
    if c == "":
        return False
    #ret = c in SPECIAL_UNIT_CHARS

    try:
        ret = c in SPECIAL_UNIT_CHARS
    except:
        #source = unicode(c, 'utf-8')
        # ascii decode fail, first encode in utf-8
        source = c.encode("utf-8")
        ret = source in SPECIAL_UNIT_CHARS
    return ret

CHAR_TYPES = [0] * 128
DIGIT    = 0x01
ALPHA_LO = 0x02
ALPHA_UP = 0x04
ALPHA    = ALPHA_UP | ALPHA_LO
UNIT     = 0x08
TZ       = 0x10
ID_START = 0x20
ID       = 0x40
SPECIAL_UNIT_CHARS = "²"

def _init_chartypes():
    for i in range(ord('a'), ord('z')+1):
        CHAR_TYPES[i] = ALPHA_LO | UNIT | TZ | ID_START | ID
    for i in range(ord('A'), ord('Z')+1):
        CHAR_TYPES[i] = ALPHA_UP | UNIT | TZ | ID
    for i in range(ord('0'), ord('9')+1):
        CHAR_TYPES[i] = DIGIT | TZ | ID

    CHAR_TYPES[ord('%')] = UNIT
    CHAR_TYPES[ord('_')] = UNIT | TZ | ID
    CHAR_TYPES[ord('/')] = UNIT
    CHAR_TYPES[ord('$')] = UNIT
    #CHAR_TYPES[ord('²')] = UNIT
    CHAR_TYPES[ord('-')] = TZ
    CHAR_TYPES[ord('+')] = TZ



_init_chartypes()



"""

        """