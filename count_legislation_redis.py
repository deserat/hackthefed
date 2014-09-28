#
# Don't assume nothing smart from this file I'm just messing around with 
# the data files and getting to know them. Anything of value will go 
# elsewhere.
# 

# TODO: Break up legistlator documents so that sub document are other collections. Write performance.

# TODO: for legislator add subject with activity count
# TODO: Map legislator to  congresses
# TODO:  Map legislator to committees


import os
import redis
import json
import multiprocessing
import socket
import redis





# TODO: when backonline load by hostname or rolename
from conf.vance import DB, DB_HOST, DB_USER, DB_PASS

#
# Settings
#

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "{0}/data/congress".format(APP_DIR)


conn = redis.Redis()


# 
# Drop collections while we play'
# 




def chunks(l, n):
    """ Yield successive n-sized chunks from a list
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def create_congresses(congresses):
    for c in congresses:
        conn.delete(c)

def process_bills(subset):
    """ Loop over bills. Count and tally statistics on congressmen 
    for each peace of legislation. """

    for subdir in subset:
        this_dir = "{0}/{1}/bills".format(DATA_DIR, subdir)
        for root, dirs, files in os.walk(this_dir):
            if "data.json" in files and "text-versions" not in root:
                file_path = "{0}/data.json".format(root)

                bill = json.loads( open(file_path, 'r').read() )
                congress = int(bill.get("congress", "0"))
                conn.hincrby(congress, bill.get("bill_type", "NO TYPE"), 1 )




if __name__ == '__main__':
    jobs = []
    dirs = os.walk(DATA_DIR).next()[1]
    #dirs = [103,104,105,106,107,108,109,110,111,112,113]
    create_congresses(dirs)
    num = len(dirs)
    procs = num / 4
    for subset in list(chunks(dirs, procs)):
        p = multiprocessing.Process(target=process_bills, args=(subset,))
        jobs.append(p)
        p.start()

