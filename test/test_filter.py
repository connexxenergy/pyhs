#!/usr/bin/env python
# coding: utf8
"""
Test HFilter
 
"""
import unittest
from hs.filter import HFilter
from hs.grid import HDictBuilder
from hs.val import HDate, HBool, HStr, HUri, HTime, HRef, HNum

class FilterTest(unittest.TestCase):

    def testIdentity(self):
        """Tests eq noteq
        """
        self.verifyEq(HFilter.has("a"), HFilter.has("a"))
        self.verifyNotEq(HFilter.has("a"), HFilter.has("b"))

    @unittest.skip("Disabled till fixed")
    def testParseZincLiterals(self):
        # TODO: make this work verify Zinc only literals do not work
        self.verifyEq(HFilter.make("x==T"), None)
        self.verifyEq(HFilter.make("x==F"), None)
        self.verifyEq(HFilter.make("x==F"), None)

    def testParse(self):

        # basics
        self.verifyParse("x", HFilter.has("x"))
        self.verifyParse("foo", HFilter.has("foo"))
        self.verifyParse("fooBar", HFilter.has("fooBar"))
        self.verifyParse("foo7Bar", HFilter.has("foo7Bar"))
        self.verifyParse("foo_bar->a", HFilter.has("foo_bar->a"))
        self.verifyParse("a->b->c", HFilter.has("a->b->c"))
        self.verifyParse("not foo", HFilter.missing("foo"))

        # bool literals
        self.verifyParse("x->y==true", HFilter.eq("x->y", HBool.TRUE))
        self.verifyParse("x->y!=false", HFilter.ne("x->y", HBool.FALSE))

        # str literals
        self.verifyParse("x==\"hi\"", HFilter.eq("x", HStr.make("hi")))
        self.verifyParse("x!=\"\\\"hi\\\"\"",  HFilter.ne("x", HStr.make("\"hi\"")))

        # TODO: this fails
        #self.verifyParse("x==\"_\\uabcd_\\n_\"", HFilter.eq("x", HStr.make("_\uabcd_\n_")))

        # uri literals
        self.verifyParse("ref==`http://foo/?bar`", HFilter.eq("ref", HUri.make("http://foo/?bar")))
        self.verifyParse("ref->x==`file name`", HFilter.eq("ref->x", HUri.make("file name")))
        self.verifyParse("ref == `foo bar`", HFilter.eq("ref", HUri.make("foo bar")))

        # int literals
        self.verifyParse("num < 4", HFilter.lt("num", n(4)))
        self.verifyParse("num <= -99", HFilter.le("num", n(-99)))

        # float literals
        self.verifyParse("num < 4.0", HFilter.lt("num", n(4.0)))

        self.verifyParse("num <= -9.6", HFilter.le("num", n(-9.6)))
        self.verifyParse("num > 400000", HFilter.gt("num", n(4e5)))
        self.verifyParse("num >= 16000", HFilter.ge("num", n(1.6e+4)))
        self.verifyParse("num >= 2.16", HFilter.ge("num", n(2.16)))

        # unit literals

        self.verifyParse("dur < 5ns", HFilter.lt("dur", n(5,"ns")))
        self.verifyParse("dur < 10kg", HFilter.lt("dur", n(10, "kg")))
        self.verifyParse("dur < -9sec", HFilter.lt("dur", n(-9, "sec")))
        self.verifyParse("dur < 2.5hr", HFilter.lt("dur", n(2.5, "hr")))

        # date, time, datetime
        self.verifyParse("foo < 2009-10-30", HFilter.lt("foo", HDate.make_from_str("2009-10-30")))
        self.verifyParse("foo < 08:30:00", HFilter.lt("foo", HTime.make_from_str("08:30:00")))
        self.verifyParse("foo < 13:00:00", HFilter.lt("foo", HTime.make_from_str("13:00:00")))

        # ref literals
        self.verifyParse("author == @xyz", HFilter.eq("author", HRef.make("xyz")))
        self.verifyParse("author==@xyz:foo.bar", HFilter.eq("author", HRef.make("xyz:foo.bar")))

        # and
        self.verifyParse("a and b", HFilter.has("a").and_(HFilter.has("b")))
        self.verifyParse("a and b and c == 3", HFilter.has("a").and_( HFilter.has("b").and_(HFilter.eq("c", n(3))) ))

        # or
        self.verifyParse("a or b", HFilter.has("a").or_(HFilter.has("b")))
        self.verifyParse("a or b or c == 3", HFilter.has("a").or_(HFilter.has("b").or_(HFilter.eq("c", n(3)))))

        # parens
        self.verifyParse("(a)", HFilter.has("a"))
        self.verifyParse("(a) and (b)", HFilter.has("a").and_(HFilter.has("b")))
        self.verifyParse("( a )  and  ( b ) ", HFilter.has("a").and_(HFilter.has("b")))
        self.verifyParse("(a or b) or (c == 3)", HFilter.has("a").or_(HFilter.has("b")).or_(HFilter.eq("c", n(3))))

        isA = HFilter.has("a")
        isB = HFilter.has("b")
        isC = HFilter.has("c")
        isD = HFilter.has("d")
        self.verifyParse("a and b or c", (isA.and_(isB)).or_(isC))
        self.verifyParse("a or b and c", isA.or_(isB.and_(isC)))
        self.verifyParse("a and b or c and d", (isA.and_(isB)).or_(isC.and_(isD)))
        self.verifyParse("(a and (b or c)) and d", isA.and_(isB.or_(isC)).and_(isD))
        self.verifyParse("(a or (b and c)) or d", isA.or_(isB.and_(isC)).or_(isD))

    def test_include(self):
        """Test include statement.
        """
        # build dicts to check
        a = HDictBuilder() \
            .add("dis", "a") \
            .add("num", 100) \
            .add("foo", 99) \
            .add("date", HDate.make(2011,10,5)) \
            .toDict()

        b = HDictBuilder() \
            .add("dis", "b") \
            .add("num", 200) \
            .add("foo", 88) \
            .add("date", HDate.make(2011,10,20)) \
            .add("bar") \
            .add("ref", HRef.make("a")) \
            .toDict()

        c = HDictBuilder() \
            .add("dis", "c") \
            .add("num", 300) \
            .add("ref", HRef.make("b")) \
            .add("bar") \
            .toDict()

        db = {
            "a": a,
            "b": b,
            "c": c,
            }

        self.verifyInclude(db, "dis",                "a,b,c")
        self.verifyInclude(db, "dis == \"b\"",       "b")
        self.verifyInclude(db, "dis != \"b\"",       "a,c")
        self.verifyInclude(db, "dis <= \"b\"",       "a,b")
        self.verifyInclude(db, "dis >  \"b\"",       "c")
        self.verifyInclude(db, "num < 200",          "a")
        self.verifyInclude(db, "num <= 200",         "a,b")
        self.verifyInclude(db, "num > 200",          "c")
        self.verifyInclude(db, "num >= 200",         "b,c")
        self.verifyInclude(db, "date",               "a,b")
        self.verifyInclude(db, "date == 2011-10-20", "b")
        self.verifyInclude(db, "date < 2011-10-10",  "a")
        self.verifyInclude(db, "foo",                "a,b")
        self.verifyInclude(db, "not foo",            "c")
        self.verifyInclude(db, "foo == 88",          "b")
        self.verifyInclude(db, "foo != 88",          "a")
        self.verifyInclude(db, "foo == \"x\"",       "")
        self.verifyInclude(db, "ref",                "b,c")

        self.verifyInclude(db, "ref->dis",           "b,c")
        self.verifyInclude(db, "ref->dis == \"a\"",  "b")
        self.verifyInclude(db, 'ref->dis == "a"',  "b")
        self.verifyInclude(db, "ref->bar",           "c")
        self.verifyInclude(db, "not ref->bar",       "a,b")
        self.verifyInclude(db, "foo and bar",        "b")
        self.verifyInclude(db, "foo or bar",         "a,b,c")
        self.verifyInclude(db, "(foo and bar) or num==300",  "b,c")
        self.verifyInclude(db, "foo and bar and num==300",   "")

    def verifyParse(self, s, expected):
        actual = HFilter.make(s)
        self.verifyEq(actual, expected)

    def verifyEq(self, a, b):
        print("verifyEq: a=%s, b=%s" % (a, b))
        self.assertEqual(a, b)

    def verifyNotEq(self, a, b):
        self.assertNotEqual(a, b)

    def verifyInclude(self, d, query, expected):
        class MyPather:
            def __init__(self, d):
                self.d = d
            def find(self, id):
                return self.d.get(id)

        print(query)
        db = MyPather(d)

        q = HFilter.make(query)
        actual = ""
        for c in "abc":
            inst = db.find(c)
            if (q.include(inst, db)):
                if len(actual):
                    actual += ","
                actual += c

        self.verifyEq(expected, actual)


def n(val, unit=None):
    return HNum.make(val, unit)

if __name__ == '__main__':
    unittest.main()

