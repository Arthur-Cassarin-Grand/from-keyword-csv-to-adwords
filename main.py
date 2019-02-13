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

import sys
import time
import argparse
import os

from googleads import adwords
from googleads.errors import *

from csv_data import *
from adwords_engine import *

# Make the match with your CSV file headings (here in french)
headings_map = {
    "text":"Expression",
    "ads_group":"Groupe",
    "targeting":"Ciblage",
    "campaign":"Campagne",
}

targeting_map = {
    "BROAD":"Large",
    "PHRASE":"Expression",
    "EXACT":"Exact",
}

def main(args):
    # Check if Python 3
    if (sys.version_info < (3, 0)):
        sys.stdout.write('This script requires Python 3.X.')
        sys.exit(1)

    parser=argparse.ArgumentParser()
    parser.add_argument('-csv','--csv', '-c', help='The CSV file that contains keywords, ads groups and campaigns.', required=True)
    parser.add_argument('-idadwords','--idadwords', '-a', help='The account Adwords that will receive new keywords, ads groups and campaigns. I.e. 123-456-7891 or 1234567891', required=True)
    parser.add_argument('-delimiter','--delimiter', '-d', help='CSV delimiter, for exemple , or ;', required=True)
    args=parser.parse_args()

    csv_file = args.csv
    filename, file_extension = os.path.splitext(csv_file)
    if file_extension != '.csv':
        print('The data file must be a CSV type format.')
        sys.exit(1)

    delimiter = args.delimiter
    customer_service_id = args.idadwords
    if '-' in customer_service_id:
        customer_service_id = customer_service_id.replace('-','')
    if len(customer_service_id) != 10 and customer_service_id.isdigit() == False:
        print('This Adwords account ID is not valid. It must be 10 digits. I.e. 123-456-7891 or 1234567891')
        sys.exit(1)

    start_time = time.time()

    # Load customer account access
    client = adwords.AdWordsClient.LoadFromStorage(path="googleads.yaml")
    client.SetClientCustomerId(customer_service_id)

    # Counters
    created_campaigns = 0
    created_ads_groups = 0
    created_keywords = 0

    # Get CSV entities (Campaigns, Ads groups, Keywords)
    csv_campaigns = get_ads_campaigns(csv_file, headings_map, delimiter)
    csv_ads_groups = get_ads_groups(csv_file, headings_map, delimiter)
    csv_keywords = get_ads_keywords(csv_file, headings_map, targeting_map, delimiter)
    nb_campaigns = str(count_elements(csv_campaigns))
    nb_ads_groups = str(count_elements(csv_ads_groups))
    nb_keywords = str(count_elements(csv_keywords))
    
    print('CSV file is OK.')
    print('Campaigns found : ' + nb_campaigns)
    print('Ads groups found : ' + nb_ads_groups)
    print('Keywords found : ' + nb_keywords)

    start_script_input = input("Do you want to import your data into Google Ads ? [Y/N] : ")
    if start_script_input == "N" or start_script_input == "n":
        sys.exit(0)
    elif start_script_input != "Y" and start_script_input != "y":
        print("Bad user input, exit script.")
        sys.exit(1)

    print('Adwords API running...')

    # --- Create campaigns
    account_campaigns = get_adwords_campaigns(client)

    for csv_campaign in csv_campaigns:
        # Check if the campaign already exists (based on it's name)
        exists = False
        for account_campaign in account_campaigns:
            if account_campaign['name'] == csv_campaign.name:
                exists = True
        if exists == False:
            # If not, create it
            print("Create '" + csv_campaign.name + "' campaign")
            create_adwords_campaign(client, csv_campaign)
            # Refresh the account campaigns's list
            account_campaigns = get_adwords_campaigns(client)
            created_campaigns += 1

        # Get the current campaign's ID
        campaign_id = get_adwords_campaign_id(client, csv_campaign.name)

        # --- Create ads groups for this campaign
        for csv_ads_group in csv_ads_groups:
            # If the ads group belongs to the campaign
            if csv_ads_group.campaign_name == csv_campaign.name:
                # Check if the ads group already exists (based on it's name)
                account_ads_groups = get_adwords_ads_groups(client, campaign_id)
                exists = False
                for account_ads_group in account_ads_groups:
                    if account_ads_group['name'] == csv_ads_group.name:
                        exists = True
                if exists == False:
                    print("Create '" + csv_ads_group.name + "' ads group")
                    create_adwords_ad_group(client, campaign_id, csv_ads_group)
                    # Refresh the account ads group's list
                    account_ads_groups = get_adwords_ads_groups(client, campaign_id)
                    created_ads_groups += 1

                # Get the current group ad's ID
                adwords_ad_group_id = get_adwords_ad_group_id(client, csv_ads_group.name, campaign_id)

                # --- Create keywords for this ads group
                for csv_keyword in csv_keywords:
                    # If the keyword belongs to the ads group
                    if csv_keyword.ads_group == csv_ads_group.name:
                        # Check if the ads group already exists (based on it's name)
                        account_ads_group_keywords = get_adwords_ads_group_keywords(
                            client,
                            adwords_ad_group_id,
                        )
                        exists = False
                        for account_ads_group_keyword in account_ads_group_keywords:
                            if account_ads_group_keyword['criterion']['text'] == csv_keyword.text:
                                exists = True
                        if exists == False:
                            print("Create '" + csv_keyword.text + "' keyword [Targeting : " + csv_keyword.targeting + "]")
                            create_adwords_keyword(client, adwords_ad_group_id, csv_keyword)
                            # Refresh the account ads group's keywords list
                            account_ads_group_keywords = get_adwords_ads_group_keywords(
                                client,
                                adwords_ad_group_id,
                            )
                            created_keywords += 1

    print('Campaigns created : ' + str(created_campaigns) + ' on ' + nb_campaigns + ' found')
    print('Ads groups created : ' + str(created_ads_groups) + ' on ' + nb_ads_groups + ' found')
    print('Keywords created : ' + str(created_keywords) + ' on ' + nb_keywords + ' found')
    processed_time = round(time.time() - start_time,2)
    print("Finished in %s seconds" % processed_time)

if __name__ == "__main__":
    main(sys.argv)
