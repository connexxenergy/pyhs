#!/usr/bin/env python
"""Navigate a site hierarchy.

usage:
./navsite.py url id password
e.g.:
./navsite.py http://localhost/test-project/haystack scott@example.com tiger

"""
import sys
from hs.client import HClient

def start_nav(client):
    """Browse the site using haystack nav command"""
    res = client.nav()
    if res.rows:
        for row in res.rows:
            do_nav(client, row, 0)

def do_nav(client, record, level):
    """Recursively navigate from given record.
    prints current node/record
    
    Args:
        client: cx API authenticated client
        record: node record
        level: indentation/recursion level
        
    Example:
    >>> do_nav(hclient, record, 0)
        Bristol Community College (@BCC)
          BCCBldgB.BldgB_RTU_B1_points_heat_ctrl (@BCC_BCCBldgB.BldgB_RTU_B1_points_heat_ctrl)
            BCCBldgB_BldgB_RTU_B1_points_heat_ctrl_1 (@H.BCCBldgB.BldgB_RTU_B1_points_heat_ctrl_1)
          BCCBldgE.BldgE_EFE1 (@BCC_BCCBldgE.BldgE_EFE1)
            BCCBldgE_BldgE_EFE1_Status (@H.BCCBldgE.BldgE_EFE1_Status)
            BCCBldgE_BldgE_EFE1_Enable (@H.BCCBldgE.BldgE_EFE1_Enable)
          BCCBldgH.BldgH_SH10 (@BCC_BCCBldgH.BldgH_SH10)
            BCCBldgH_BldgH_SH10_ReturnHumidity (@H.BCCBldgH.BldgH_SH10_ReturnHumidity)
            BCCBldgH_BldgH_SH10_nviRmHeatSpt (@H.BCCBldgH.BldgH_SH10_nviRmHeatSpt)
            BCCBldgH_BldgH_SH10_OptStartCommand (@H.BCCBldgH.BldgH_SH10_OptStartCommand)

    
    """
    #print('level=%d'%level)
    tab = "  " * level
    s = "%s%s (%s)" % (tab, record.get('dis'), record.get('id'))
    # print with indenting based on level
    print(s)
    if record.get('navId'):
        res = client.nav(record['navId'])
        if res.rows:
            for row in res.rows:
                do_nav(client, row, level+1)
        
    
def main(argv=None):
    client = HClient(argv[1], argv[2], argv[3])
    #res = client.about()    
    start_nav(client)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    

