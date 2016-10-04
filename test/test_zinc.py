#!/usr/bin/env python
# coding: utf8
"""
Test zinc read and writer

"""
import unittest
import json
import csv
import StringIO
from hs.grid import HDict, HDictBuilder
from hs.val import HMarker, HStr, HDateTime, HDate, HTime, HTimeZone, HNum, HRef
from hs.io import ZincReader, ZincWriter, JsonWriter, CsvWriter


grid1 = """ver:"2.0"
fooBar33

"""
grid2 = """ver:"2.0" tag foo:"bar"
xyz
"val"

"""


zinc_hisWriteMulti = \
"""ver:"2.0"
ts,v0 id:@a,v1 id:@b
2012-04-21T08:30:00-04:00 New_York,72.2,76.3
2012-04-21T08:45:00-04:00 New_York,N,76.3
"""

zinc_hisWriteMulti_b = \
"""ver:"2.0"
ts,v0 id:@a,v1 id:@b
2012-04-21T08:30:00-04:00 New_York,72.2,76.3
2012-04-21T08:45:00-04:00 New_York,,76.3
"""

# TODO: add these additional use cases from unit test test_cxapi.py
"""
PAYLOAD_HISWRITE = \
ver:"2.0" id:@Test-point-002
ts,val
2010-06-07T01:00:00-05:00 Chicago,73.3
2010-06-07T02:00:00-05:00 Chicago,75.5

PAYLOAD_HISWRITE2 = \
ver:"2.0" id:@Test-point-004
ts,val
2010-06-08T01:00:00-05:00 Chicago,T
2010-06-08T02:00:00-05:00 Chicago,F
2010-06-08T03:00:00-05:00 Chicago,F
2010-06-08T04:00:00-05:00 Chicago,F
2010-06-08T05:00:00-05:00 Chicago,T

# payload for multipoint hisWrite
PAYLOAD_MHISWRITE = \
ver:"2.0"
ts,v0 id:@Test-point-002,v1 id:@Test-point-003
2012-04-21T08:30:00-04:00 New_York,72.2,76.3
2012-04-21T08:45:00-04:00 New_York,N,77.3

PAYLOAD_MHISWRITE2 = \
ver:"2.0"
ts,v0 id:@Test-point-002,v1 id:@Test-point-004
2012-04-22T08:30:00-04:00 New_York,72.2,T
2012-04-22T08:45:00-04:00 New_York,N,F
2012-04-22T09:00:00-04:00 New_York,73.5,N
2012-04-22T09:15:00-04:00 New_York,74,F
2012-04-22T09:30:00-04:00 New_York,75,T
"""



# this gernerates error in ZincRead
zinc_hisRead_err1 = \
    """ver:"2.0" hisEnd:lastMonth hisStart:lastMonth id:@Gaithersburg.RTU-2.ZoneTemp
    ts,val
    2015-10-01T00:00:00Z UTC,74.1102523804
    2015-10-01T00:15:00Z UTC,74.1204071045
    2015-10-01T00:30:00Z UTC,74.1232452393
    """

"""
orig: 'ver:"2.0" hisEnd:2015-10-01T00:30:00Z UTC hisStart:2015-10-01T00:00:00Z UTC id:@Gaithersburg.RTU-2.ZoneTemp
ts,val
2015-10-01T00:00:00Z UTC,74.1102523804
2015-10-01T00:15:00Z UTC,74.1204071045
2015-10-01T00:30:00Z UTC,74.1232452393
'
new: 'ver:"2.0" hisEnd:2015-10-01T00:30:00Z UTC hisStart:2015-10-01T00:00:00Z UTC id:@Gaithersburg.RTU-2.ZoneTemp
ts,val
2015-10-01T00:00:00Z UTC,74.1103
2015-10-01T00:15:00Z UTC,74.1204
2015-10-01T00:30:00Z UTC,74.1232
"""

# this reads fine
zinc_hisRead2 = \
"""ver:"2.0" hisEnd:"lastMonth" hisStart:"lastMonth" id:@Gaithersburg.RTU-2.ZoneTemp
ts,val
2015-10-01T00:00:00Z UTC,74.1102523804
2015-10-01T00:15:00Z UTC,74.1204071045
2015-10-01T00:30:00Z UTC,74.1232452393
"""

#     """ver:"2.0" hisEnd:"2015-10-01T00:30:00Z UTC" hisStart:"2015-10-01T00:00:00Z UTC" id:@Gaithersburg.RTU-2.ZoneTemp

zinc_hisRead = \
"""ver:"2.0" hisEnd:2015-10-01T00:30:00Z UTC hisStart:2015-10-01T00:00:00Z UTC id:@Gaithersburg.RTU-2.ZoneTemp
ts,val
2015-10-01T00:00:00Z UTC,74.1102523804
2015-10-01T00:15:00Z UTC,74.1204071045
2015-10-01T00:30:00Z UTC,74.1232452393
"""


zinc_hisRead3 = \
"""ver:"2.0" id:@Gaithersburg.RTU-2.ZoneTemp hisStart:2015-11-27T00:00:00-05:00 New_York hisEnd:2015-11-28T00:00:00-05:00 New_York
ts,val
2015-11-27T00:15:00-05:00 New_York,67.2741
2015-11-27T00:30:00-05:00 New_York,67.0864
2015-11-27T00:45:00-05:00 New_York,66.8988
2015-11-27T01:00:00-05:00 New_York,66.7113
2015-11-27T01:15:00-05:00 New_York,66.524
2015-11-27T01:30:00-05:00 New_York,66.3368
2015-11-27T01:45:00-05:00 New_York,66.1498
2015-11-27T02:00:00-05:00 New_York,65.9629
2015-11-27T02:15:00-05:00 New_York,65.777
"""

err1 = \
"""ver:"2.0" dis:"org.projecthaystack.ParseException: Invalid date time range: today1" errTrace:"org.projecthaystack.ParseException Invalid date time range: today1\n  at org.projecthaystack.server.HServer.hisRead(HServer.java:328)\n  at \org.projecthaystack.server.HisReadOp.onService(HStdOps.java:315)\n  at org.projecthaystack.server.HOp.onService(HOp.java:49)\n  at com.company.hs.CdHServlet.onService(CdHServlet.java:169)\n  at org.projecthaystack.server.HServlet.doGet(HServlet.java:46)\n  at javax.servlet.http.HttpServlet.service(HttpServlet.java:104)\n  at javax.servlet.http.HttpServlet.service(HttpServlet.java:45)\n  at winstone.ServletConfiguration.execute(ServletConfiguration.java:249)\n  at winstone.RequestDispatcher.forward(RequestDispatcher.java:335)\n  at winstone.RequestHandlerThread.processRequest(RequestHandlerThread.java:244)\n  at winstone.RequestHandlerThread.run(RequestHandlerThread.java:150)\n  at java.lang.Thread.run(Thread.java:745)\n" err
empty
"""

err2 = \
"""ver:"2.0" errTrace:"none" err dis:"Only simple axon expressions supported."
empty
"""



# doesn't work:
err2_a = \
    """ver:"2.0" errTrace:"none" err dis:Only simple axon expressions supported.
    empty
    """

all_single_grid_payloads = [ grid1, grid2, zinc_hisRead2, zinc_hisRead, zinc_hisRead3, err2,  ]

# these don't pass zinc read test:
to_fix = [ zinc_hisRead_err1, err1,  ]

multigrid = \
    """ver:"2.0"
header_label,header_value,type
"KPIs","RECENT","list"
ver:"2.0"
value,label
"1000 KWH","KWH USED"
"100 KW","KW PEAK"
"$199.95","ENERGY CHARGE"
"$199.95","ENERGY CHARGE"
"""

class ZincTest(unittest.TestCase):

    def setUp(self):
        pass

    def testNum(self):
        """Test HNum zinc rendering."""
        self.verifyZinc(HNum.NaN, "NaN")
        self.verifyZinc(HNum.POS_INF, "INF")
        self.verifyZinc(HNum.NEG_INF, "-INF")
        self.verifyZinc(HNum.make(float("nan")), "NaN")
        self.verifyZinc(HNum.make(float("inf")), "INF")
        self.verifyZinc(HNum.make(float("-inf")), "-INF")


    def test_csv(self):
        for s in all_single_grid_payloads:
            self.verifyCsvWrite(s)

    def test_multigrid_csv(self):
        self.verifyCsvMultiWrite(multigrid)
        self.verifyCsvMultiWrite(zinc_hisRead3)



    def test_json(self):
        for s in all_single_grid_payloads:
            self.verifyJsonWrite(s)

    def verifyJsonWrite(self, s):
        """Verifies json writer can write the given grid correctly.
        """
        grid = ZincReader(s).readGrid()
        json_out = JsonWriter.gridToString(grid)
        #print("json_out: '%s'" % json_out)
        # for now just verify this is valid json
        json.loads(json_out)

    def verifyCsvWrite(self, s):
        """Verifies csv writer can write the given grid correctly.
        """
        grid = ZincReader(s).readGrid()
        csv_out = CsvWriter.gridToString(grid)
        #print("csv_out: '%s'" % csv_out)
        # for now just verify this is valid csv
        #json.loads(csv_out)
        reader = csv.reader(StringIO.StringIO(csv_out))
        #print("csv after parse:")
        for i, row in enumerate(reader):
            self.assertEqual(len(row), grid.num_cols())
            #print(row)
        self.assertEqual(i, grid.num_rows())

    def verifyCsvMultiWrite(self, s):
        """Verifies csv writer can write the given grids correctly.
        """
        grids = ZincReader(s).readGrids()
        csv_out_multi = CsvWriter.gridsToString(grids)
        #print("csv_out_multi: '%s'" % csv_out_multi)
        # cummulative rows/cols:
        row_counts = map(lambda x: x.num_rows(), grids)
        total_rows = reduce(lambda x, y: x+y, row_counts)
        col_counts = map(lambda x: x.num_cols(), grids)
        max_cols = reduce(lambda x, y: max(x, y), col_counts)

        # verify csv after parsing matches number total number of rows + 1, and cols
        reader = csv.reader(StringIO.StringIO(csv_out_multi))
        #print("csv multi after parse:")
        for i, row in enumerate(reader):
            #self.assertEqual(len(row), max_cols)
            #print(row)
            pass
        # i + 1 = csv rows
        grid_count = len(grids)
        csv_total_rows = i + 1
        # grid_count because csv has a header row for each grid and a separator line for each (grid_count-1)
        self.assertEqual(csv_total_rows-2*grid_count+1, total_rows)


    def test_multigrid_json(self):
        grids = ZincReader(multigrid).readGrids()
        json_out_multi = JsonWriter.gridsToString(grids)
        #print("json_out_multi: '%s'" % json_out_multi)
        # for now just verify this is valid json
        json.loads(json_out_multi)

    def test_multigrid(self):
        """Test multigrid read
        """

        grids = ZincReader(multigrid).readGrids()
        self.assertEqual(len(grids), 2)

        self.verifyGrid(multigrid,
                        None,
                        [ ("header_label", HDictBuilder().toDict()), ("header_value", HDictBuilder().toDict()),
                          ("type", HDictBuilder().toDict())],
                        [
                        [ HStr.make("KPIs"),
                            HStr.make("RECENT"),
                            HStr.make("list"),
                        ]
                        ]
        )

        self.verifyMultiGrid(multigrid, 0,
                        None,
                        [ ("header_label", HDictBuilder().toDict()), ("header_value", HDictBuilder().toDict()),
                          ("type", HDictBuilder().toDict())],
                        [
                            [ HStr.make("KPIs"),
                              HStr.make("RECENT"),
                              HStr.make("list"),
                              ]
                        ]
        )

        self.verifyMultiGrid(multigrid, 1,
                             None,
                             [ ("value", HDictBuilder().toDict()), ("label", HDictBuilder().toDict()),
                               ],
                             [
                                [ HStr.make("1000 KWH"),
                                   HStr.make("KWH USED"),
                                ],
                                [ HStr.make("100 KW"),
                                  HStr.make("KW PEAK"),
                                  ],
                                [ HStr.make("$199.95"),
                                  HStr.make("ENERGY CHARGE"),
                                  ],
                                [ HStr.make("$199.95"),
                                  HStr.make("ENERGY CHARGE"),
                                  ],
                             ]
        )




    #@unittest.skip("Disabled while testing other functions")
    def test_singlegrid(self):
        """Test single grid read
        """
        self.verifyGrid(err2,
                        HDictBuilder().add("errTrace", "none").add("err").add("dis", "Only simple axon expressions supported."),
                        [("empty",  {})],
            []
        )



        self.verifyGrid(zinc_hisRead,
            HDictBuilder().add("id", HRef.make("Gaithersburg.RTU-2.ZoneTemp")).
               add("hisStart", HDateTime.make(HDate.make(2015,10,1), HTime.make(0,0,0), HTimeZone.make("UTC"), 0)).
               add("hisEnd", HDateTime.make(HDate.make(2015,10,1), HTime.make(0,30,0), HTimeZone.make("UTC"), 0)).
               toDict(),
            [("ts", HDictBuilder().toDict()), ("val", HDictBuilder().toDict())],
            [
                # note: insignificate digits will be truncated - see
                #   http://stackoverflow.com/questions/2440692/formatting-floats-in-python-without-superfluous-zeros
                [HDateTime.make(HDate.make(2015,10,1), HTime.make(0,0,0), HTimeZone.make("UTC"), 0), HNum.make(74.1103)],
                [HDateTime.make(HDate.make(2015,10,1), HTime.make(0,15,00), HTimeZone.make("UTC"), 0), HNum.make(74.1204)],
                [HDateTime.make(HDate.make(2015,10,1), HTime.make(0,30,00), HTimeZone.make("UTC"), 0), HNum.make(74.1232)],
                #[HDateTime.make(HDate.make(2015,10,1), HTime.make(0,0,0), HTimeZone.make("UTC"), 0), HNum.make(74.1102523804)],
                #[HDateTime.make(HDate.make(2015,10,1), HTime.make(0,15,00), HTimeZone.make("UTC"), 0), HNum.make(74.1204071045)],
                #[HDateTime.make(HDate.make(2015,10,1), HTime.make(0,30,00), HTimeZone.make("UTC"), 0), HNum.make(74.1232452393)],
                ]
        )

        self.verifyGrid(zinc_hisWriteMulti,
            None,
            [("ts", HDictBuilder().toDict()), ("v0", HDictBuilder().add("id", HRef.make("a")).toDict()), ("v1",  HDictBuilder().add("id", HRef.make("b")).toDict())],
            [
            [HDateTime.make(HDate.make(2012,4,21), HTime.make(8,30,0), HTimeZone.make("New_York"), -14400),
                HNum.make(72.2), HNum.make(76.3)],
            [HDateTime.make(HDate.make(2012,4,21), HTime.make(8,45,0), HTimeZone.make("New_York"), -14400),
                None, HNum.make(76.3)],
            ]
            )

        self.verifyGrid(zinc_hisWriteMulti_b,
                        None,
                        [("ts", HDictBuilder().toDict()), ("v0", HDictBuilder().add("id", HRef.make("a")).toDict()), ("v1",  HDictBuilder().add("id", HRef.make("b")).toDict())],
                        [
                            [HDateTime.make(HDate.make(2012,4,21), HTime.make(8,30,0), HTimeZone.make("New_York"), -14400),
                             HNum.make(72.2), HNum.make(76.3)],
                            [HDateTime.make(HDate.make(2012,4,21), HTime.make(8,45,0), HTimeZone.make("New_York"), -14400),
                             None, HNum.make(76.3)],
                            ]
        )

        self.verifyGrid(grid1, None, [("fooBar33", HDictBuilder().toDict())], [])
        self.verifyGrid(grid2,
            HDictBuilder().add("tag", HMarker.VAL).add("foo", HStr.make("bar")).toDict(),
            [("xyz", {})],
            [
            [HStr.make("val")],
            ]
        )



    def verifyGrid(self, s, meta, cols, rows):
        # normalize nulls
        if not meta:
            meta = HDict.EMPTY
        for i in range(len(cols)):
            if not cols[i]:
                cols[i] = HDict.EMPTY

        # read from zinc
        grid = ZincReader(s).readGrid()
        #self.verifyGridEq(grid, meta, cols, rows)

        # write grid and verify we can parse that too
        writestr = ZincWriter.gridToString(grid)
        print("orig: '%s'" % s)
        print("new: '%s'" % writestr)
        write_grid = ZincReader(writestr).readGrid()
        self.verifyGridEq(write_grid, meta, cols, rows)

    def verifyMultiGrid(self, s, grid_index, meta, cols, rows):
        """Verify given grid within multigrid.
        """
        # normalize nulls
        if not meta:
            meta = HDict.EMPTY
        for i in range(len(cols)):
            if not cols[i]:
                cols[i] = HDict.EMPTY

        # read from zinc
        grids = ZincReader(s).readGrids()
        self.assertLess(grid_index, len(grids))
        grid = grids[grid_index]
        #self.verifyGridEq(grid, meta, cols, rows)

        # write grid and verify we can parse that too
        writestr = ZincWriter.gridToString(grid)
        writestrmulti = ZincWriter.gridsToString(grids)
        print("orig: '%s'" % s)
        print("new for multigrid: '%s'" % writestrmulti)
        print("new for single grid: '%s'" % writestr)
        write_grid = ZincReader(writestr).readGrid()
        self.verifyGridEq(write_grid, meta, cols, rows)


    def verifyGridEq(self, grid, meta, cols, rows):
        self.assertEqual(grid.meta, meta)
        self.assertEqual(grid.num_cols(), len(cols))

        # cols
        for i, col in enumerate(grid.cols):
            self.assertEqual(col.name, cols[i][0])
            self.assertEqual(col.meta, cols[i][1])

        # rows
        self.assertEqual(grid.num_rows(), len(rows))
        for i, row in enumerate(grid.rows):
            expected = rows[i]
            for ci in range(len(expected)):
                #print expected[ci], row.get(grid.col(ci).name)
                self.assertEqual(expected[ci], row.get(grid.col(ci).name))


    def verifyZinc(self, hval, zinc_str):
        """Verify zinc for hval renders properly.
        """
        self.assertEqual(hval.to_zinc(), zinc_str)


if __name__ == '__main__':
    unittest.main()

