import os
import json
import multiprocessing
import pandas as pd
import numpy as np

from multiprocessing import Pool


DATA_DIR = "./data/congress"


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


def crawl_congresses(congress):
    """
    A container function that recurses a set of directory and extracts data data from the
    legislation contained therein.

    :return dict: A Dictionary of DataFrames
    """

    # DataFrames we are going to return see https://github.com/deserat/hackthefed/wiki/Legislative%20DataModel
    # for more info

    # Core Data
    legislation = pd.DataFrame()

    # Relationships

    bills_per_congress = pd.DataFrame()
    sponsors = pd.DataFrame()
    cosponsors = pd.DataFrame()
    committees = pd.DataFrame()
    ammendments = pd.DataFrame()
    subjects = pd.DataFrame()
    titles = pd.DataFrame()

    # Change Log
    actions = pd.DataFrame()

    bills = "{0}/{1}/bills".format(DATA_DIR, congress)
    for root, dirs, files in os.walk(bills):
        if "data.json" in files and "text-versions" not in root:
            file_path = "{0}/data.json".format(root)
            bill = json.loads(open(file_path, 'r').read())

            # let's start with just the legislative information

            extract_legislation(bill)


if __name__ == '__main__':
    jobs = []
    dirs = os.walk(DATA_DIR).next()[1]
    p = Pool(2)
    print dirs
    p.map(crawl_congresses, dirs)
