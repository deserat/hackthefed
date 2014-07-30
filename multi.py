import os
import multiprocessing

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = "{0}/data/congress".format(APP_DIR)


def worker(d):
    """thread worker function"""
    print 'Directory:', d
    return
def process_bills(subset):
# Loop over bills. Count and tally statistics on congressmen 
# for each peace of legislation.

    for subdir in subset:
        this_dir = "{0}/{1}".format(DATA_DIR, subdir)
        print this_dir

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

if __name__ == '__main__':
    jobs = []
    dirs = os.walk(DATA_DIR).next()[1]
    num = len(dirs)
    procs = num / 4
    for subset in list(chunks(dirs, procs)):
        p = multiprocessing.Process(target=process_bills, args=(subset,))
        jobs.append(p)
        p.start()