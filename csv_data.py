# Copyright 2019 Arthur Cassarin-Grand
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import sys

from googleads import adwords

DEFAULT_ADS_CAMPAIGN_BUDGET = 100000 # Equal to 0,10€/$/etc.
DEFAULT_ADS_GROUP_BID_AMOUNT = 100000

class AdsCampaign(object):
    def __init__(self, name, budget):
        self.name = name
        self.budget = budget

    def __eq__(self, other):
        return self.name == other.name

class AdsGroup(object):
    def __init__(self, name, bid_amount, campaign):
        self.name = name
        self.bid_amount = bid_amount
        self.campaign_name = campaign

    def __eq__(self, other):
        return self.name == other.name

class AdsKeyword(object):
    def __init__(self, text, targeting, ads_group):
        self.text = text
        self.targeting = targeting
        self.ads_group = ads_group

    def __eq__(self, other):
        return self.text == other.text and self.targeting == other.targeting

"""
Prevent illegal caracters for Google Adwords API
"""
def clear_string_for_api(text):
    text = text.replace("’","'")
    illegal_caracters = [
        "@",
        "!",
        ",",
        "%",
        "^",
        "*",
        "(",
        ")",
        "=",
        "{",
        "}",
        "~",
        "`",
        "<",
        ">",
        "?",
        "|"
    ]

    for illegal_caracter in illegal_caracters:
        text = text.replace(illegal_caracter, "")

    return text

"""
To count campaigns/ads groups/keywords loaded in CSV file
"""
def count_elements(elements):
    return len(elements)

"""
Add the item in the given list if the item doesn't already exists.
"""
def add_item_if_not_exists(item, items_list):
    exists = False
    for element in items_list:
        if element == item:
            exists = True
    if exists == False:
        items_list.append(item)

"""
Return a keyword into broad modified (+) format
I.e : super keyword -> +super +keyword
"""
def get_broad_modified(keyword):
    keyword = '+' + keyword
    keyword = keyword.replace(' ', ' +')
    return keyword

"""
Return a list of AdsCampaign() with no duplicates.
"""
def get_ads_campaigns(file, headings_map, delimiter):
    campaigns_group = []
    with open(file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
        line_counter = 0
        for row in csv_reader:
            line_counter += 1
            # Check integrity
            try:
                if row[headings_map['campaign']] == '':
                    print('The campaign n°' + str(line_counter) + ' has no name.')
                    sys.exit(1)
            except KeyError:
                print('The CSV delimiter must be wrong or the CSV file doesn\'t respect the heading map (see main.py file).')
                sys.exit(1)
            # Create entity
            campaign = AdsCampaign(
                clear_string_for_api(row[headings_map['campaign']]),
                DEFAULT_ADS_CAMPAIGN_BUDGET
            )
            add_item_if_not_exists(campaign, campaigns_group)
    return campaigns_group

"""
Return a list of AdsGroup() with no duplicates.
"""
def get_ads_groups(file, headings_map, delimiter):
    ads_group = []
    with open(file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
        line_counter = 0
        for row in csv_reader:
            line_counter += 1
            # Check integrity
            if row[headings_map['ads_group']] == '':
                print('The ads group n°' + str(line_counter) + ' has no name.')
                sys.exit(1)
            if row[headings_map['campaign']] == '':
                print('The ads group n°' + str(line_counter) + ' has no campaign.')
                sys.exit(1)
            # Create entity
            ad_group = AdsGroup(
                clear_string_for_api(row[headings_map['ads_group']]),
                DEFAULT_ADS_GROUP_BID_AMOUNT,
                clear_string_for_api(row[headings_map['campaign']])
            )
            add_item_if_not_exists(ad_group, ads_group)
    return ads_group

"""
Return a list of AdsKeyword() with no duplicates.
"""
def get_ads_keywords(file, headings_map, targeting_map, delimiter):
    ads_keywords = []
    with open(file, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file, delimiter=delimiter)
        line_counter = 0
        for row in csv_reader:
            line_counter += 1
            # Check integrity
            if row[headings_map['targeting']] == '':
                print('The keyword n°' + str(line_counter) + ' has no targeting.')
                sys.exit(1)
            if row[headings_map['text']] == '':
                print('The keyword n°' + str(line_counter) + ' has no text.')
                sys.exit(1)
            if row[headings_map['ads_group']] == '':
                print('The keyword n°' + str(line_counter) + ' has no ads group.')
                sys.exit(1)
            # Create entity
            targeting = row[headings_map['targeting']]
            # Match targeting with Google Ads API criterion
            if targeting == targeting_map['BROAD']:
                targeting = 'BROAD'
            elif targeting == targeting_map['PHRASE']:
                targeting = 'PHRASE'
            elif targeting == targeting_map['EXACT']:
                targeting = 'EXACT'
            elif targeting == targeting_map['BPE']:
                targeting = 'BPE'
            else:
                print('The keyword n°' + str(line_counter) + ' has an invalid targeting (must match the heading_targeting pattern).')
                sys.exit(1)
            keyword = AdsKeyword(
                clear_string_for_api(row[headings_map['text']]),
                targeting,
                clear_string_for_api(row[headings_map['ads_group']])
            )
            add_item_if_not_exists(keyword, ads_keywords)
    return ads_keywords
