import os
import sys
import json
import multiprocessing
import logging
import traceback
import os.path
import pandas as pd
import numpy as np
import pandas_lib as pl


from datetime import datetime, date
from multiprocessing import Pool


DATA_DIR = "./data/congress"
OUT_DIR = "./data/csv"


class Congress(object):
    name = None
    legislation = None

    def __init__(self, name):
        self.name = name


def datestring_to_datetime(string):
    d_array = [int(x) for x in "2011-02-03".split("-")].extend([0, 0])
    if d_array:
        return datetime(*d_array)
    else:
        return None


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
    bill_id = bill.get('bill_id', None)
    for co in cosponsors:
        co_list = []
        co_list.append(co.get('thomas_id'))
        co_list.append(bill_id)
        co_list.append(co.get('district'))
        co_list.append(co.get('state'))
        cosponsor_map.append(co_list)
    logger.debug("End Extractioning Cosponsors")
    return cosponsor_map


def extract_subjects(bill):
    """
    Return a list subject for legislation.
    """
    logger.debug("Extracting Subjects")
    subject_map = []
    subjects = bill.get('subjects', [])
    bill_id = bill.get('bill_id', None)
    bill_type = bill.get('bill_type', None)
    for sub in subjects:
        subject_map.append((bill_id, bill_type, sub))
    logger.debug("End Extractioning Subjects")
    return subject_map


def extract_committees(bill):
    """
    Returns committee associations from a bill.
    """
    bill_id = bill.get('bill_id', None)
    logger.debug("Extracting Committees for {0}".format(bill_id))

    committees = bill.get('committees', None)
    committee_map = []

    for c in committees:
        logger.debug("Processing committee {0}".format(c.get('committee_id')))
        c_list = []
        sub = c.get('subcommittee_id')
        if sub:
            logger.debug("is subcommittee")
            c_list.append('subcommittee')  # type
            c_list.append(c.get('subcommittee'))
            sub_id = "{0}-{1}".format(c.get('committee_id'), c.get('subcommittee_id'))
            logger.debug("Processing subcommittee {0}".format(sub_id))
            c_list.append(sub_id)
        else:
            c_list.append('committee')
            c_list.append(c.get('committee'))
            c_list.append(c.get('committee_id'))
        c_list.append(bill_id)
        committee_map.append(c_list)
    return committee_map


# Really don't like how this is comming together.....
def extract_events(bill):
    """
    Returns all events  from legislations. Thing of this as a log for congress.

    There are alot of events that occur around legislation. For now we are
    going to kepe it simple. Introduction, cosponsor, votes dates
    """
    events = []
    logger.debug(events)

    bill_id = bill.get('bill_id', None)
    if bill_id:
        logger.debug('got bill id')
        intro_date = datestring_to_datetime(bill.get('introduced_at', None))
        sponsor = bill.get('sponsor', None)
        type = sponsor.get('type', None)
        id = bill.get('thomas_id', None)
        events.append((bill_id, 'introduced', type, id, intro_date))

    logger.debug(events)

    return events


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
            try:

                record = extract_legislation(bill)
                legislation.append(record)

                sponsor = extract_sponsor(bill)
                sponsors.append(sponsor)

                cosponsor = extract_cosponsors(bill)
                cosponsors.extend(cosponsor)

                subject = extract_subjects(bill)
                subjects.extend(subject)

                # evts = extract_events(bill)
                # events.append(evts)

                committee = extract_committees(bill)
                committees.extend(committee)

            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.debug(exc_type, fname, exc_tb.tb_lineno)
    try:

        congress_obj.legislation = pd.DataFrame(legislation)
        congress_obj.legislation.columns = [
            'congress', 'bill_id', 'bill_type', 'enacted_as', 'active', 'active_at',
            'awaiting_signature', 'enacted', 'vetoed', 'introduced_at', 'number',
            'official_title', 'popular_title', 'short_title', 'status', 'status_at',
            'top_subject', 'updated_at'
        ]

        congress_obj.sponsors = pd.DataFrame(sponsors)
        congress_obj.sponsors.columns = [
            'type', 'thomas_id', 'bill_id', 'district', 'state'
        ]

        congress_obj.cosponsors = pd.DataFrame(cosponsors)
        congress_obj.sponsors.columns = [
            'type', 'thomas_id', 'bill_id', 'district', 'state'
        ]

        congress_obj.committees = pd.DataFrame(committees)
        congress_obj.committees.columns = [
            'type', 'name', 'committee_id', 'bill_id'
        ]

        congress_obj.subjects = pd.DataFrame(subjects)
        congress_obj.subjects.columns = [
            'bill_id', 'bill_type', 'subject'
        ]

        # congress_obj.events = pd.DataFrame(events)
        pl.save_congress(congress_obj)
        # print "{0} - {1}".format(congress, len(legislation))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger.debug(e)
        logger.debug(exc_tb.tb_lineno)
        logger.debug(exc_type, fname, exc_tb.tb_lineno)


if __name__ == '__main__':
    logger = multiprocessing.log_to_stderr()
    logger.setLevel(logging.INFO)
    jobs = []
    # dirs = [c for c in os.walk(DATA_DIR).next()[1] if int(c) > 100]
    dirs = range(100, 114)
    p = Pool(12)

    try:
        p.map_async(crawl_congress, dirs).get(999999)
    except KeyboardInterrupt:
        pool.terminate()
        print "You cancelled the program!"
        sys.exit(1)
