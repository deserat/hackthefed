import os
import pandas as pd
import yaml  # Ruby users should die.
import logging

DATA_DIR = "./data"

#
# Legislator Functions
#


def import_legislators():
    """
    Read the legislators from the csv files into a single Dataframe. Intended for importing new data.
    """
    current = pd.DataFrame().from_csv("{0}/congress-legislators/legislators-current.csv".format(DATA_DIR))
    historic = pd.DataFrame().from_csv("{0}/congress-legislators/legislators-historic.csv".format(DATA_DIR))
    legislators = current.append(historic)

    # more than one thing has a thomas_id so it's kinda usless in our model
    legislators['legislator_id'] = legislators['thomas_id']

    return legislators


def save_legislators(legislators):
    """
    Output legislators datafrom to csv.
    """
    legislators.to_csv("{0}/csv/legislators.csv".format(DATA_DIR), encoding='utf-8')


#
# Committee Functions
#

def import_committees():
    """
    Read the committees from the csv files into a single Dataframe. Intended for importing new data.
    """
    committees = []
    subcommittees = []

    with open("{0}/congress-legislators/committees-current.yaml".format(DATA_DIR), 'r') as stream:
        committees += yaml.load(stream)

    with open("{0}/congress-legislators/committees-current.yaml".format(DATA_DIR), 'r') as stream:
        committees += yaml.load(stream)

    # Sub Committees are not Committees
    # And unfortunately the good folk at thomas thought modeling data with duplicate id's was a good idea.
    # you can have two subcommittees with the ID 12. Makes a simple membership map impossible.
    for com in committees:

        com['committee_id'] = com['thomas_id']

        if 'subcommittees' in com:
            # process sub committees into separate DataFrame
            for subcom in com.get('subcommittees'):
                subcom['committee_id'] = com['thomas_id']  # we use committee_id so we can easily merge dataframes
                subcom['subcommittee_id'] = "{0}-{1}".format(subcom['committee_id'], subcom['thomas_id'])
                subcommittees.append(subcom)

            del com['subcommittees']

    committees_df = pd.DataFrame(committees)
    subcommittees_df = pd.DataFrame(subcommittees)

    return [committees_df, subcommittees_df]


def save_committees(committees):
    """
    Output legislators datafrom to csv.
    """
    committees.to_csv("{0}/csv/committees.csv".format(DATA_DIR), encoding='utf-8')


def save_subcommittees(subcommittees):
    """
    Output legislators datafrom to csv.
    """
    subcommittees.to_csv("{0}/csv/subcommittees.csv".format(DATA_DIR), encoding='utf-8')


def make_congress_dir(congress):
    congress_dir = "{0}/csv/{1}".format(DATA_DIR, congress)
    path = os.path.dirname(congress_dir)
    print "{0} path exists".format(congress_dir)
    if not os.path.exists(congress_dir):
        os.mkdir(congress_dir)
    return congress_dir


def save_congress(congress):
    """
    Takes a congress object with legislation, sponser, cosponsor, commities
    and subjects attributes and saves each item to it's own csv file.
    """
    try:
        congress_dir = make_congress_dir(congress.name)
        congress.legislation.to_csv("{0}/legislation.csv".format(congress_dir), encoding='utf-8')
        congress.sponsors.to_csv("{0}/sponsor_map.csv".format(congress_dir), encoding='utf-8')
        congress.cosponsors.to_csv("{0}/cosponsor_map.csv".format(congress_dir), encoding='utf-8')
        # congress.events.to_csv("{0}/events.csv".format(congress_dir), encoding='utf-8')
        congress.committees.to_csv("{0}/committees_map.csv".format(congress_dir), encoding='utf-8')
        congress.subjects.to_csv("{0}/subjects_map.csv".format(congress_dir), encoding='utf-8')
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


def import_committee_membership():
    with open("{0}/congress-legislators/committee-membership-current.yaml".format(DATA_DIR), 'r') as stream:
        c_membership = yaml.load(stream)

    members = []

    for c in c_membership:
        for member in c_membership[c]:
            member['committee_id'] = c
            member['title'] = member.get('title', 'Member')
            member['party_position'] = member['party']
            member['legislator_id'] = int(member['thomas'])
            del(member['party'])
            del(member['thomas'])
            members.append(member)

    return pd.DataFrame(members)


def save_committee_membership(membership):
    membership.to_csv("{0}/csv/membership.csv".format(DATA_DIR), encoding='utf-8')
