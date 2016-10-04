#!/usr/bin/env python
# coding: utf8
"""
Test HDict

 
"""
import unittest
from hs import grid
from hs.grid import HDict, HDictBuilder
from hs.val import HRef, HDate, HMarker, HStr, HNum
from hs.io import ZincReader

class DictTest(unittest.TestCase):

    def testEmpty(self):
        """Tests empty HDict
        """
        tags = grid.HDictBuilder().toDict()
        # size
        self.assertEqual(tags, grid.HDict.EMPTY)
        self.assertTrue(tags == grid.HDict.EMPTY)
        # missing tag
        self.assertFalse(tags.has("foo"))
        self.assertTrue(tags.missing("foo"))
        self.assertIsNone(tags.get("foo"))

    def testIstagname(self):
        self.assertFalse(grid.istagname(""))
        self.assertFalse(grid.istagname("A"))
        self.assertFalse(grid.istagname(" "))
        self.assertTrue(grid.istagname("a"))
        self.assertTrue(grid.istagname("a_B_19"))
        self.assertFalse(grid.istagname("a b"))
        self.assertFalse(grid.istagname("a\u0128"))
        self.assertFalse(grid.istagname("a\u0129x"))
        self.assertFalse(grid.istagname("a\uabcdx"))

    def testBasics(self):
        db = grid.HDictBuilder()
        tags = db.add("id", HRef.make("aaaa-bbbb")).add("site") \
            .add("geoAddr", "Richmond, Va") \
            .add("area", 1200, "ft") \
            .add("date", HDate.make(2000, 12, 3)) \
            .toDict()
        #print d
        # size
        self.assertEqual(len(tags), 5)
        self.assertFalse(tags.is_empty())

        # configured tags
        #print tags.get("id"), HRef.make("aaaa-bbbb")
        self.assertEqual(tags.get("id"), HRef.make("aaaa-bbbb"))
        self.assertEqual(tags.get("site"), HMarker.VAL)
        self.assertEqual(tags.get("geoAddr"), HStr.make("Richmond, Va"))
        self.assertEqual(tags.get("area"), HNum.make(1200, "ft"))
        self.assertEqual(tags.get("date"),  HDate.make(2000, 12, 3))

        # missing tags
        self.assertFalse(tags.is_empty())
        self.assertFalse(tags.has("foo"))
        self.assertTrue(tags.missing("foo"))
        self.assertIsNone(tags.get("foo"))

    def testEquality(self):
        a = grid.HDictBuilder().add("x").toDict()
        self.assertEqual(a,  grid.HDictBuilder().add("x").toDict())
        self.assertNotEqual(a,  grid.HDictBuilder().add("x", 3).toDict())
        self.assertNotEqual(a,  grid.HDictBuilder().add("y").toDict())
        self.assertNotEqual(a,  grid.HDictBuilder().add("x").add("y").toDict())

        a = grid.HDictBuilder().add("x").add("y", "str").toDict()
        self.assertEqual(a,  grid.HDictBuilder().add("x").add("y", "str").toDict())
        self.assertEqual(a,  grid.HDictBuilder().add("y", "str").add("x").toDict())
        self.assertNotEqual(a,  grid.HDictBuilder().add("x", "str").add("y", "str").toDict())
        self.assertNotEqual(a, grid.HDictBuilder().add("x").add("y", "strx").toDict())
        self.assertNotEqual(a, grid.HDictBuilder().add("y", "str").toDict())
        self.assertNotEqual(a, grid.HDictBuilder().add("x").toDict())
        self.assertNotEqual(a, grid.HDictBuilder().add("x").add("yy", "str").toDict())


    def testZinc(self):
        self.verifyZinc("", HDict.EMPTY)
        self.verifyZinc("foo_12", HDictBuilder().add("foo_12").toDict())
        #self.verifyZinc("fooBar:123ft", HDictBuilder().add("fooBar", 123, "ft").toDict())
        self.verifyZinc('dis:"Bob" bday:1970-06-03 marker',
                        HDictBuilder().add("dis", "Bob").add("bday", HDate.make(1970,6,3)).add("marker").toDict())
        self.verifyZinc('dis  :  "Bob"  bday : 1970-06-03  marker',
                        HDictBuilder().add("dis", "Bob").add("bday", HDate.make(1970,6,3)).add("marker").toDict())

    def testDis(self):
        self.assertEqual(grid.HDictBuilder().add("id", HRef.make("a")).toDict().dis, "a")
        self.assertEqual(grid.HDictBuilder().add("id", HRef.make("a", "b")).toDict().dis, "b")
        self.assertEqual(grid.HDictBuilder().add("id", HRef.make("a")).add("dis", "d").toDict().dis, "d")


    def verifyZinc(self, s, tags):
        x = ZincReader(s).readDict()
        if len(tags) <= 1:
            self.assertEqual(x, tags)


"""

"""

if __name__ == '__main__':
    unittest.main()

