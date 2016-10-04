#!/usr/bin/env python
# coding: utf8
"""
Test grid

 
"""
import unittest
from hs import grid
from hs.val import HRef, HDate, HMarker, HStr, HNum
from hs.io import ZincWriter

class GridTest(unittest.TestCase):

    def setUp(self):
        pass


    def testEmpty(self):
        """Tests grid
        """
        g = grid.HGridBuilder().toGrid()
        #self.assertEqual(g, grid.HGrid.EMPTY)
        self.assertEqual(g.meta, grid.HDict.EMPTY)
        self.assertEqual(g.num_rows(), 0)

        self.assertTrue(g.is_empty())
        self.assertEqual(g.col("foo"), None)
        try:
            g.col("foo")
            self.fail('g.col("foo") should raise exception')
        except:
            # ok
            pass

    def testNoRows(self):
        b = grid.HGridBuilder()
        b.meta.add("dis", "Title")
        b.addCol("a").add("dis", "Alpha")
        b.addCol("b")
        g = b.toGrid()
        gridstr = ZincWriter.gridToString(g)
        print(gridstr)

        # meta
        self.assertEqual(len(g.meta), 1)
        self.assertEqual(g.meta.get("dis"), HStr.make("Title"))

        # cols
        self.assertEqual(g.num_cols(), 2)
        c = self.verifyCol(g, 0, "a")
        self.assertEqual(c.dis, "Alpha")
        self.assertEqual(len(c.meta), 1)
        self.assertEqual(c.meta.get("dis"), HStr.make("Alpha"))

        # rows
        self.assertEqual(g.num_rows(), 0)
        self.assertTrue(g.is_empty())

        # iterator
        self.verifyGridIterator(g)

    def testSimple(self):
        """Similar to Java test, but doesn't support raising exceptions in getters:

                try { r.get("fooBar"); fail(); } catch (UnknownNameException e) { verifyException(e); }

        """
        b = grid.HGridBuilder()
        b.addCol("id")
        b.addCol("dis")
        b.addCol("area")
        b.addRow( [HRef.make("a"), HStr.make("Alpha"), HNum.make(1200)])
        b.addRow( [HRef.make("b"), HStr.make("Beta"), None])

        # meta
        g = b.toGrid()
        self.assertEqual(len(g.meta), 0)
        gridstr = ZincWriter.gridToString(g)
        print(gridstr)
        # cols
        self.assertEqual(g.num_cols(), 3);
        self.verifyCol(g, 0, "id");
        self.verifyCol(g, 1, "dis");
        self.verifyCol(g, 2, "area");

        # rows
        self.assertEqual(g.num_rows(), 2);
        self.assertFalse(g.is_empty());
        r = g.row(0)
        self.assertEqual(r.get("id"), HRef.make("a"))
        self.assertEqual(r.get("dis"), HStr.make("Alpha"))
        self.assertEqual(r.get("area"), HNum.make(1200))
        r = g.row(1)
        self.assertEqual(r.get("id"), HRef.make("b"))
        self.assertEqual(r.get("dis"), HStr.make("Beta"))
        self.assertEqual(r.get("area"), None)

        self.assertEqual(r.get("fooBar"), None);

        # HRow.iterator no-nulls
        it = iter(g.row(0))
        self.verifyRowIterator(it, "id", HRef.make("a"))
        self.verifyRowIterator(it, "dis",  HStr.make("Alpha"))
        self.verifyRowIterator(it, "area", HNum.make(1200))
        try:
            it.next()
            self.fail('it.next() should raise exception after exhausting the g.row(0) iterator')
        except StopIteration:
            pass

        # HRow.iterator with nulls


        it = iter(g.row(1))
        self.verifyRowIterator(it, "id",  HRef.make("b"))
        self.verifyRowIterator(it, "dis", HStr.make("Beta"))

        try:
            it.next()
            self.fail('it.next() should raise exception after exhausting the g.row(1) iterator')
        except StopIteration:
            pass


        # iterator
        self.verifyGridIterator(g)

    def test_other_ops(self):
        hdicts = []
        d = grid.HDictBuilder() \
            .add("id", HRef.make("aaaa-bbbb")).add("site") \
            .add("geoAddr", "Richmond, Va") \
            .add("area", 1200, "ft") \
            .add("date", HDate.make(2000, 12, 3)) \
            .toDict()
        hdicts.append(d)
        grid.HGridBuilder().dictsToGrid(grid.HDict.EMPTY, hdicts)

    def verifyCol(self, g, i, n):
        col = g.col(i)
        self.assertEqual(col, g.col(n))
        self.assertEqual(col.name, n)
        return col

    def verifyGridIterator(self, g):
        i = 0
        for i, row in enumerate(g):
            #print row
            self.assertEqual(g.rows[i], row)
        if i:
            self.assertEqual(g.num_rows(), i+1)
        it = iter(g)
        i = 0
        for row in it:
            self.assertEqual(g.rows[i], row)
            i += 1
        self.assertEqual(g.num_rows(), i)
        try:
            it.next()
            self.fail('it.next() should raise exception after exhausting the iterator')
        except StopIteration:
            pass

    def verifyRowIterator(self, it, name, val):
        """Similar to Java test, but doesn't support check for hasNext, since that is against
        the Python patterns.
         """
        item = it.next()
        #self.assertEqual(item.name, name)
        self.assertEqual(item, val)



if __name__ == '__main__':
    unittest.main()

