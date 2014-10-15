import pandas as pd
import yaml # Ruby users should die.

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

    return current.append(historic)

def save_legislators(legislators):
    """
    Output legislators datafrom to csv.
    """
    legislators.to_csv("{0}/csv/legislators.csv".format(DATA_DIR))


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

        if com.has_key('subcommittees'):

            # process sub committees into separate DataFrame
            for subcom in com.get('subcommittees'):
                subcom['committee_id'] = com['thomas_id']  # we use committee_id so we can easily merge dataframes
                subcom['subcommittee_id'] = "{0}-{1}".format(subcom['committee_id'], subcom['thomas_id'])
                print subcom
                subcommittees.append(subcom)

            del com['subcommittees']

    print subcommittees

    committees_df = pd.DataFrame(committees)
    subcommittees_df = pd.DataFrame(subcommittees)

    return [committees_df, subcommittees_df]

def save_committees(committees):
    """
    Output legislators datafrom to csv.
    """
    committees.to_csv("{0}/csv/committees.csv".format(DATA_DIR))

def save_subcommittees(subcommittees):
    """
    Output legislators datafrom to csv.
    """
    subcommittees.to_csv("{0}/csv/subcommittees.csv".format(DATA_DIR))


def import_committee_membership():
    with open("{0}/congress-legislators/committee-membership-current.yaml".format(DATA_DIR), 'r') as stream:
        c_membership = yaml.load(stream)

    return pd.DataFrame(c_membership)
