"""
Implementation of HFilter related classes.

"""
import StringIO
from io import ZincReader as zr
from val import HRef

class ZincReader(zr):

    def readFilter(self):
        self._init_grid_read()
        self.is_filter = True
        self._skipSpace()
        q = self.readFilterOr()
        self._skipSpace()
        if self.cur != "":
            raise ValueError("Expected end of stream")
        return q

    def readFilterOr(self):
        q = self.readFilterAnd()
        self._skipSpace()
        if (self.cur != 'o'): return q
        if not self._readId() ==  "or": raise ValueError("Expecting 'or' keyword")
        self._skipSpace()
        return q.or_(self.readFilterOr())


    def readFilterAnd(self):
        q = self.readFilterAtomic()
        self._skipSpace()
        if (self.cur != 'a'): return q
        if not self._readId() ==  "and": raise ValueError("Expecting 'and' keyword")
        self._skipSpace()
        return q.and_(self.readFilterAnd())

    def readFilterParens(self):
        self._consume()
        self._skipSpace()
        q = self.readFilterOr()
        if self.cur != ')': raise ValueError("Expecting ')'")
        self._consume()
        return q

    def readFilterPath(self):
        id = self._readId()
        if self.cur != '-' or self.peek != '>':
            return id

        sio = StringIO.StringIO()
        sio.write(id)
        #acc = []
        #acc.append(id)
        while self.cur == '-' or self.peek == '>':
            self._consume()
            self._consume()
            id = self._readId()
            #acc.append(id)
            sio.write("->")
            sio.write(id)
        return sio.getvalue()

    def readFilterAtomic(self):
        self._skipSpace();
        if (self.cur == '('): return self.readFilterParens()

        path = self.readFilterPath()
        self._skipSpace()

        if path.__str__() == "not":
           return HFilter.missing(self.readFilterPath())

        if self.cur == '=' and self.peek == '=':
            self._consumeCmp()
            return HFilter.eq(path, self._readVal())
        if self.cur == '!' and self.peek == '=':
            self._consumeCmp()
            return HFilter.ne(path, self._readVal())
        if self.cur == '<' and self.peek == '=':
            self._consumeCmp()
            return HFilter.le(path, self._readVal())
        if self.cur == '>' and self.peek == '=':
            self._consumeCmp()
            return HFilter.ge(path, self._readVal())
        if self.cur == '<':
            self._consumeCmp()
            return HFilter.lt(path, self._readVal())
        if self.cur == '>':
            self._consumeCmp()
            return HFilter.gt(path, self._readVal())

        return HFilter.has(path);

############################################################
######################### Initialization ###################
############################################################

# initialize unit character table


############################################################
################### Internal Helper Functions ##############
############################################################

############################################################
######################## Public Functions ##################
############################################################



############################################################
########################### Classes ########################
############################################################

class HFilter(object):

    def __init__(self):
        self.string = None

    def __str__(self):
        if self.string == None:
            self.string = self.to_str()

    def to_str(self):
        raise NotImplementedError("Subclass of HFilter has to implement: %s" % type(self))

    def __eq__(self, other):
        """Equality is based on string encoding."""
        if not (isinstance(other,  HFilter)):
            return False
        return self.__str__() == other.__str__()

    def __ne__(self, other):
        """Equality is based on string encoding."""
        if not (isinstance(other,  HFilter)):
            return True
        return self.__str__() != other.__str__()

    """
        In java, this interface is used:
      public interface Pather
      {
        /**
         * Given a HRef string identifier, resolve to an entity's
         * HDict respresentation or ref is not found return null.
         */
        public HDict find(String ref);
      }

    """

    @staticmethod
    def make(s):
        return ZincReader(s).readFilter()

    ########### Factories #############


    @staticmethod
    def has(path):
        """
        Match records which have the specified tag path defined.
        :param path:
        :return: HFilter insance
        """
        return Has(Path.make(path))


    @staticmethod
    def missing(path):
        """
        Match records which do not define the specified tag path.
        :param path:
        :return: HFilter instance
        """
        return Missing(Path.make(path))

    @staticmethod
    def eq(path, val):
        """
        Match records which have a tag are equal to the specified value.
        :param path:
        :param val: HVal instance
        :return: HFilter instance
        """
        return Eq(Path.make(path), val)

    @staticmethod
    def ne(path, val):
        """
        Match records which have a tag not equal to the specified value.
        :param path:
        :param val: HVal instance
        :return: HFilter instance
        """
        return Ne(Path.make(path), val)

    @staticmethod
    def lt(path, val):
        """
        Match records which have tags less than the specified value.
        :param path:
        :param val: HVal instance
        :return: HFilter instance
        """
        return Lt(Path.make(path), val)

    @staticmethod
    def le(path, val):
        """
        Match records which have tags less than or equals to specified value.
        :param path:
        :param val: HVal instance
        :return: HFilter instance
        """
        return Le(Path.make(path), val)

    @staticmethod
    def gt(path, val):
        """
        Match records which have tags greater than specified value.
        :param path:
        :param val: HVal instance
        :return: HFilter instance
        """
        return Gt(Path.make(path), val)

    @staticmethod
    def ge(path, val):
        """
        Match records which have tags greater than or equal to specified value.
        :param path:
        :param val: HVal instance
        :return: HFilter instance
        """
        return Ge(Path.make(path), val)

    def and_(self, that):
        """
        Operator and: Return a query which is the logical-and of this and that query.
        :param that:
        :return: HFilter instance
        """
        return And(self, that)

    def or_(self, that):
        """
        Operator or: Return a query which is the logical-or of this and that query.
        :param that:
        :return: HFilter instance
        """
        return Or(self, that)


############################################################
#################### Path Related Classes ##################
############################################################

"""

Java Pather which is not needed in Python

  /** Pather is a callback interface used to resolve query paths. */
  public interface Pather
  {
    /**
     * Given a HRef string identifier, resolve to an entity's
     * HDict respresentation or ref is not found return null.
     */
    public HDict find(String ref);
  }

"""

class Path(object):
    """Path is a simple name or a complex path using the "->" separator.
    """

    def __init__(self, path, names):
        self.path = path
        self.names = names

    @staticmethod
    def make(path):
        """Construct a new Path from string or throw ParseException.

        Examples:
            Path.make("a->b->c")
            Path.make("a")
        """
        names = path.split("->")
        return Path(path, names)

    def size(self):
        return len(self.names)

    def get(self, index):
        return self.names[index]

    def __str__(self):
        return self.path



############################################################
################### HFilter Related Classes ################
############################################################


class PathFilter(HFilter):

    def __init__(self, p):
        self.path = p

    def include(self, d, pather):
        """

        :param d: hdict
        :param pather: Pather instance
        :return: bool True if
        """
        val = d.get(self.path.get(0))
        if self.path.size() != 1:
            nt = d
            for name in self.path.names[1:]:
                if not isinstance(val, HRef):
                    val = None
                    break
                nt = pather.find(val.val)
                if nt is None:
                    val = None
                    break
                val = nt.get(name)

        return self.do_include(val)

    def do_include(self, val):
        raise NotImplementedError("Subclass of PathFilter must override do_include.")

class Has(PathFilter):

    def do_include(self, val):
        return val != None

    def __str__(self):
        return self.path.__str__()

class Missing(PathFilter):
    def do_include(self, val):
        return val == None
    def __str__(self):
        return "not %s" % self.path

class CmpFilter(PathFilter):

    def __init__(self, p, val):
        super(CmpFilter, self).__init__(p)
        self.val = val

    def same_type(self, val):
        return val is not None and type(val) == type(self.val)

    def cmp_str(self):
        raise NotImplementedError("Subclass of CmpFilter must to override cmp_str.")

    def __str__(self):
        sio = StringIO.StringIO()
        sio.write(self.path)
        sio.write(self.cmp_str())
        sio.write(self.val.to_zinc())
        return sio.getvalue()


class Eq(CmpFilter):
    """Eq filter.
    """

    def cmp_str(self):
        return "=="

    def do_include(self, val):
        return val != None and val == self.val

class Ne(CmpFilter):
    """Ne filter.
    """

    def cmp_str(self):
        return "!="

    def do_include(self, val):
        return val != None and val != self.val

class Lt(CmpFilter):
    """Lt filter.
    """

    def cmp_str(self):
        return "<"

    def do_include(self, val):
        return self.same_type(val) and val < self.val

class Le(CmpFilter):
    """Le filter.
    """

    def cmp_str(self):
        return "<="

    def do_include(self, val):
        return self.same_type(val) and val <= self.val


class Gt(CmpFilter):
    """Gt filter.
    """

    def cmp_str(self):
        return ">"

    def do_include(self, val):
        return self.same_type(val) and val > self.val


class Ge(CmpFilter):
    """Ge filter.
    """

    def cmp_str(self):
        return ">="

    def do_include(self, val):
        return self.same_type(val) and val >= self.val


class CompoundFilter(HFilter):

    def __init__(self, a, b):
        self.a = a
        self.b = b

    def keyword(self):
        raise NotImplementedError("Subclass of CompoundFilter must to override keyword.")

    def __str__(self):
        deep = isinstance(self.a, CompoundFilter) or isinstance(self.b, CompoundFilter)
        sio = StringIO.StringIO()
        if isinstance(self.a, CompoundFilter):
            sio.write("(")
            sio.write(self.a)
            sio.write(")")
        else:
            sio.write(self.a)
        sio.write(" ")
        sio.write(self.keyword())
        sio.write(" ")
        if isinstance(self.b, CompoundFilter):
            sio.write("(")
            sio.write(self.b)
            sio.write(")")
        else:
            sio.write(self.b)

        return sio.getvalue()

class And(CompoundFilter):
    def keyword(self):
        return "and"
    def include(self, d, pather):
        return self.a.include(d, pather) and self.b.include(d, pather)

class Or(CompoundFilter):
    def keyword(self):
        return "or"
    def include(self, d, pather):
        return self.a.include(d, pather) or self.b.include(d, pather)
