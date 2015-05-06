__author__ = 'siy'

import csv


def csv_to_list(csv_input):
    """
    Loads csv into a list of maps
    :param csv_input:
    :return: list of maps
    """
    out = []
    with open(csv_input) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            out.append(row)
    return out