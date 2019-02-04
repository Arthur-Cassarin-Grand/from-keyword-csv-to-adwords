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

import datetime

from googleads import adwords
from csv_data import AdsCampaign, AdsGroup, AdsKeyword

ADWORDS_VERSION = 'v201809'
PAGE_SIZE = 1000

"""
Get customer ID with the right pattern.
"""
def get_adwords_customer_id(customer_id):
    return customer_id.replace('-','')

"""
Return all Adwords campaign from the CM Adwords Account.
"""
def get_adwords_all_customers_from_account(client):
    managed_customer_service = client.GetService(
      'ManagedCustomerService', version=ADWORDS_VERSION)

    offset = 0
    selector = {
        'fields': ['CustomerId', 'Name'],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }
    more_pages = True
    accounts = {}
    child_links = {}
    parent_links = {}
    root_account = None

    while more_pages:
        page = managed_customer_service.get(selector)
        if 'entries' in page and page['entries']:
            if 'links' in page:
                for link in page['links']:
                    if link['managerCustomerId'] not in child_links:
                        child_links[link['managerCustomerId']] = []
                        child_links[link['managerCustomerId']].append(link)
                    if link['clientCustomerId'] not in parent_links:
                        parent_links[link['clientCustomerId']] = []
                        parent_links[link['clientCustomerId']].append(link)
            for account in page['entries']:
                accounts[account['customerId']] = account
        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])

    for customer_id in accounts:
        if customer_id not in parent_links:
            root_account = accounts[customer_id]

    return accounts

# ----------------

"""
Create an Adwords campaign.
"""
def create_adwords_campaign(client, campaign: AdsCampaign):
    campaign_service = client.GetService('CampaignService', version=ADWORDS_VERSION)
    budget_service = client.GetService('BudgetService', version=ADWORDS_VERSION)

    budget = {
        'name': campaign.name,
        'amount': {
            'microAmount': campaign.budget,
        },
        'deliveryMethod': 'STANDARD',
        'isExplicitlyShared': False, # Budget only for this campaign
    }

    budget_operations = [{
        'operator': 'ADD',
        'operand': budget
    }]

    budget_id = budget_service.mutate(budget_operations)['value'][0][
        'budgetId']

    operations = [{
        'operator': 'ADD',
        'operand': {
            'name': campaign.name,
            'status': 'ENABLED',
            'advertisingChannelType': 'SEARCH',
            'biddingStrategyConfiguration': {
                'biddingStrategyType': 'MANUAL_CPC',
            },
            'endDate': (datetime.datetime.now() +
                        datetime.timedelta(365)).strftime('%Y%m%d'),
            'budget': {
                'budgetId': budget_id
            },
            'networkSetting': {
              'targetGoogleSearch': 'true',
              'targetSearchNetwork': 'true',
              'targetContentNetwork': 'false',
              'targetPartnerSearchNetwork': 'false'
            },
        }
    }]
    campaigns = campaign_service.mutate(operations)

"""
Create an Adwords ad group.
"""
def create_adwords_ad_group(client, campaign_id, ad_group: AdsGroup):
    ad_group_service = client.GetService('AdGroupService', version=ADWORDS_VERSION)

    operations = [{
        'operator': 'ADD',
        'operand': {
            'campaignId': campaign_id,
            'name': ad_group.name,
            'status': 'ENABLED',
            'biddingStrategyConfiguration': {
                'bids': [
                    {
                        'xsi_type': 'CpcBid',
                        'bid': {
                            'microAmount': ad_group.bid_amount
                        },
                    }
                ]
            },
            'settings': [
                {
                    'xsi_type': 'TargetingSetting',
                    'details': [
                        {
                            'xsi_type': 'TargetingSettingDetail',
                            'criterionTypeGroup': 'PLACEMENT',
                            'targetAll': 'false',
                        },
                        {
                            'xsi_type': 'TargetingSettingDetail',
                            'criterionTypeGroup': 'VERTICAL',
                            'targetAll': 'true',
                        },
                    ]
                }
            ]
        }
    }]
    ad_groups = ad_group_service.mutate(operations)

"""
Create an Adwords keyword.
"""
def create_adwords_keyword(client, ad_group_id, keyword: AdsKeyword):
    ad_group_criterion_service = client.GetService(
        'AdGroupCriterionService', version=ADWORDS_VERSION)

    keyword1 = {
        'xsi_type': 'BiddableAdGroupCriterion',
        'adGroupId': ad_group_id,
        'criterion': {
            'xsi_type': 'Keyword',
            'matchType': keyword.targeting,
            'text': keyword.text
        }
    }

    operations = [
        {
            'operator': 'ADD',
            'operand': keyword1
        }
    ]
    ad_group_criteria = ad_group_criterion_service.mutate(
        operations)['value']

# ----------------

"""
Get adwords campaigns from a customer account.
Returns a dict (id, name, status).
"""
def get_adwords_campaigns(client):
    campaign_service = client.GetService('CampaignService', version=ADWORDS_VERSION)
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        },
    }

    page = campaign_service.get(selector)
    return page['entries']

"""
Get adwords ads group from a campaign.
Returns a dict (id, name, status).
"""
def get_adwords_ads_groups(client, campaign_id):
    ad_group_service = client.GetService('AdGroupService', version=ADWORDS_VERSION)
    offset = 0
    selector = {
        'fields': ['Id', 'Name', 'Status'],
        'predicates': [
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': [campaign_id]
            }
        ],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        },
    }

    page = ad_group_service.get(selector)
    return page['entries']

"""
Get adwords ads group's keyword from a customer account.
Returns a dict (id, name, status).
"""
def get_adwords_ads_group_keywords(client, adgroup_id):
    ad_group_criterion_service = client.GetService('AdGroupCriterionService', version=ADWORDS_VERSION)
    offset = 0
    selector = {
        'fields': ['Id', 'CriteriaType', 'KeywordMatchType', 'KeywordText'],
        'predicates': [
            {
                'field': 'AdGroupId',
                'operator': 'EQUALS',
                'values': [adgroup_id]
            },
            {
                'field': 'CriteriaType',
                'operator': 'EQUALS',
                'values': ['KEYWORD']
            }
        ],
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        },
        'ordering': [{'field': 'KeywordText', 'sortOrder': 'ASCENDING'}]
    }
    page = ad_group_criterion_service.get(selector)
    return page['entries']

# ----------------

"""
Get the Adwords campaign ID.
"""
def get_adwords_campaign_id(client, campaign_name):
    account_campaigns = get_adwords_campaigns(client)
    for account_campaign in account_campaigns:
        if account_campaign['name'] == campaign_name:
            return account_campaign['id']
    return None

"""
Get the Adwords ad group ID.
"""
def get_adwords_ad_group_id(client, ad_group_name, campaign_id):
    account_group_ads = get_adwords_ads_groups(client, campaign_id)
    for account_group_ad in account_group_ads:
        if account_group_ad['name'] == ad_group_name:
            return account_group_ad['id']
    return None