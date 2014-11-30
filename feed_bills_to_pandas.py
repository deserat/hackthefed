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
    Returns a list of the legislation fields we need for our legislation DataFrame

    :param bill:
    :return list:
    """

    record = []
    record.append(bill.get('congress', None))
    record.append(bill.get('bill_id', None))
    record.append(bill.get('bill_type', None))
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


def extract_sponsor(bill):
    """
    Return a list of the fields we need to map a sponser to a bill
    """
    logger.debug("Extracting Sponsor")
    sponsor_map = []
    sponsor = bill.get('sponsor', None)
    if sponsor:
        sponsor_map.append(sponsor.get('type'))
        sponsor_map.append(sponsor.get('thomas_id'))
        sponsor_map.append(bill.get('bill_id'))
        sponsor_map.append(sponsor.get('district'))
        sponsor_map.append(sponsor.get('state'))
    logger.debug("END Extracting Sponsor")
    return sponsor_map


def extract_cosponsors(bill):
    """
    Return a list of list relating cosponsors to legislation.
    """
    logger.debug("Extracting Cosponsors")
    cosponsor_map = []
    cosponsors = bill.get('cosponsors', [])
    for co in cosponsors:
        cosponsor_map.append(co.get('thomas_id'))
        cosponsor_map.append(co.get('bill_id'))
        cosponsor_map.append(co.get('district'))
        cosponsor_map.append(co.get('state'))
    logger.debug("End Extractioning Cosponsors")
    return cosponsor_map


def extract_events(bill):
    """
    Returns all events  from legislations. Thing of this as a log for congress.
    """
    return [()]


def crawl_congress(congress):
    """
    A container function that recurses a set of directory and extracts data from
    the legislation contained therein.

    :return dict: A Dictionary of DataFrames
    """

    logger = multiprocessing.log_to_stderr()
    logger.setLevel(logging.DEBUG)

    logger.info("Begin processing {0}".format(congress))

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
    events = []

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

            sponsor = extract_sponsor(bill)
            sponsors.append(sponsor)

            cosponsor = extract_sponsor(bill)
            cosponsors.append(cosponsor)

            evts = extract_events(bill)
            events.append(evts)

    congress_obj.legislation = pd.DataFrame(legislation)
    congress_obj.sponsors = pd.DataFrame(sponsors)
    congress_obj.cosponsors = pd.DataFrame(cosponsors)
    congress_obj.events = pd.DataFrame(events)

    pl.save_congress(congress_obj)
    # print "{0} - {1}".format(congress, len(legislation))


if __name__ == '__main__':
    logger = multiprocessing.log_to_stderr()
    logger.setLevel(logging.DEBUG)
    jobs = []
    dirs = os.walk(DATA_DIR).next()[1]
    p = Pool(12)
    try:
        p.map_async(crawl_congress, dirs).get(999999)
    except KeyboardInterrupt:
        pool.terminate()
        print "You cancelled the program!"
        sys.exit(1)
