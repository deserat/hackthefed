import os
import json
import multiprocessing
import pandas as pd
import numpy as np
import logging
import pandas_lib as pl

from multiprocessing import Pool


DATA_DIR = "./data/congress"
OUT_DIR = "./data/csv"


class Congress(object):
    name = None
    legislation = None

    def __init__(self, name):
        self.name = name


def extract_legislation(bill):
    """
    Returns an array of the legislation fields we need for our legislation DataFrame

    :param bill:
    :return list:
    """

    record = []
    record.append(bill.get('congress', None))
    record.append(bill.get('bill_id', None))
    record.append(bill.get('enacted_as', None))
    record.append(bill.get('active', None))
    record.append(bill.get('active_at', None))
    record.append(bill.get('awaiting_signature', None))
    record.append(bill.get('enacted', None))
    record.append(bill.get('vetoed', None))
    record.append(bill.get('introduced_at', None))
    record.append(bill.get('number', None))
    record.append(bill.get('official_title', None))
    record.append(bill.get('popular_title', None))
    record.append(bill.get('short_title', None))
    record.append(bill.get('status', None))
    record.append(bill.get('status_at', None))
    record.append(bill.get('top_subject', None))
    record.append(bill.get('updated_at', None))

    return record


def crawl_congress(congress):
    """
    A container function that recurses a set of directory and extracts data from
    the legislation contained therein.

    :return dict: A Dictionary of DataFrames
    """

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(logging.INFO)

    logger.info(congress)

    congress_obj = Congress(congress)
    # We construct lists that can be used to construct dataframes.  Adding to
    # dataframes is expensive so we don't do  that.

    # Core Data
    legislation = []

    # Relationships
    bills_per_congress = []
    sponsors = []
    cosponsors = []
    committees = []
    ammendments = []
    subjects = []
    titles = []

    # Change Log
    actions = pd.DataFrame()

    bills = "{0}/{1}/bills".format(DATA_DIR, congress)
    index = 0

    for root, dirs, files in os.walk(bills):
        if "data.json" in files and "text-versions" not in root:
            file_path = "{0}/data.json".format(root)
            bill = json.loads(open(file_path, 'r').read())

            # let's start with just the legislative information

            record = extract_legislation(bill)
            legislation.append(record)

    congress_obj.legislation = pd.DataFrame(legislation)
    pl.save_congress(congress_obj)
    # print "{0} - {1}".format(congress, len(legislation))


if __name__ == '__main__':
    logger = multiprocessing.log_to_stderr()
    logger.setLevel(logging.INFO)
    jobs = []
    dirs = os.walk(DATA_DIR).next()[1]
    p = Pool(12)
    try:
        p.map_async(crawl_congress, dirs).get(999999)
    except KeyboardInterrupt:
        pool.terminate()
        print "You cancelled the program!"
        sys.exit(1)
