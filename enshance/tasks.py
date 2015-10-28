#  Celery tasks for enshance
from __future__ import unicode_literals

import os
import furl
import json
import logging

from celery import Celery
from sharepa import ShareSearch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "enshance.settings")
from enshance import requests
from enshance import settings
from orcid.models import GatheredContributor

app = Celery()
app.config_from_object(settings)

ORCID_BASE_URL = 'http://pub.orcid.org/v1.2/search/orcid-bio?q='
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get(d, key, default=None):
    if d:
        try:
            return d[key]
        except KeyError:
            return default
    else:
        return None


def debug(func):
    def inner(*args, **kwargs):
        import ipdb
        with ipdb.launch_ipdb_on_exception():
            return func(*args, **kwargs)
    return inner


@app.task(rate_limit=1)
def gather_email_orcid(start):
    all_people = GatheredContributor.objects.order_by('id').exclude(id_email__isnull=True).exclude(id_email__exact='').iterator()
    if start:
        all_people = all_people.filter(id__gte=start).iterator()
    for count, person in enumerate(all_people):
        if person.id_email:
            query_orcid_one_email.delay(person.id, person.id_email)


@app.task(rate_limit=1)
def gather_email_from_orcid(start):
    all_people = GatheredContributor.objects.order_by('id').filter(id_orcid__isnull=False)
    if start:
        all_people = all_people.filter(id__gte=start).iterator()
    for count, person in enumerate(all_people):
        query_orcid_one_id.delay(person.id, person.id_orcid)


@app.task(rate_limit=1)
def query_orcid_one_email(db_id, email):
    email_search_url = ORCID_BASE_URL + 'email:{}'.format(email)
    orcid_data = requests.get(email_search_url, headers={'Accept': 'application/orcid+json'}).json()
    if orcid_data['orcid-search-results']['num-found'] == 1:
        contributor = GatheredContributor.objects.get(id=db_id)

        contributor.id_orcid = orcid_data['orcid-search-results']['orcid-search-result'][0]['orcid-profile']['orcid-identifier']['uri']
        contributor.raw_orcid = orcid_data['orcid-search-results']['orcid-search-result']
        contributor.save()

        if db_id % 1000 == 0:
            logger.info('Last queried person id: {}'.format(db_id))


@app.task
def pull_names_from_raw_orcid():
    has_orcid_info = GatheredContributor.objects.filter(raw_orcid__isnull=False)

    count = 0
    for person in has_orcid_info:
        save_one_person.delay(person)

        count += 1

        if count % 100 == 0:
            logger.info('Processed {} contributors.'.format(count))


@app.task
def save_one_person(person):
    details = person.raw_orcid[0]['orcid-profile']['orcid-bio']['personal-details']

    orcid_given = details.get('given-names')
    orcid_family = details.get('family-name')
    orcid_addional = details.get('other-names')
    orcid_credit = details.get('credit-name')

    person.orcid_given_name = get(orcid_given, 'value')
    person.orcid_family_name = get(orcid_family, 'value')
    person.orcid_additional_name = get(orcid_addional, 'value')
    person.orcid_name = get(orcid_credit, 'value')

    person.save()


@app.task(rate_limit=1)
def query_orcid_one_id(db_id, orcid):
    orcid_number = furl.furl(orcid).pathstr[1:]
    orcid_search_url = ORCID_BASE_URL + 'orcid:{}'.format(orcid_number)

    orcid_data = requests.get(orcid_search_url, headers={'Accept': 'application/orcid+json'}).json()
    if orcid_data['orcid-search-results']['num-found'] == 1:
        contributor = GatheredContributor.objects.get(id=db_id)

        email = None
        contact_details = orcid_data['orcid-search-results']['orcid-search-result'][0]['orcid-profile']['orcid-bio'].get('contact-details')
        if contact_details:
            email_list = contact_details['email']
            for email in email_list:
                if email['current']:
                    email = email['value']

        contributor.id_email = email
        contributor.raw_orcid = orcid_data['orcid-search-results']['orcid-search-result']
        contributor.save()

    if db_id % 1000 == 0:
        logger.info('Last queried person id: {}'.format(db_id))


@app.task
def gather_contributors(start=None):
    client = ShareSearch().sort('providerUpdatedDateTime')
    if start:
        client = client.filter('range', providerUpdatedDateTime={'gte': start})

    results = client.scan(size=1000)

    for count, result in enumerate(results):
        for contributor in result.contributors:
            reconstructed_name = get(contributor, 'givenName', '')
            if get(contributor, 'additionalName'):
                reconstructed_name = '{} {}'.format(reconstructed_name.strip(), contributor['additionalName'])
            reconstructed_name = '{} {}'.format(reconstructed_name.strip(), get(contributor, 'familyName'))
            orcid = None
            if get(contributor, 'sameAs'):
                for identifier in get(contributor, 'sameAs'):
                    if 'orcid' in identifier:
                        orcid = identifier
            GatheredContributor.objects.create(
                raw_name=contributor['name'],
                name=reconstructed_name,
                family_name=get(contributor, 'familyName'),
                given_name=get(contributor, 'givenName'),
                additional_name=get(contributor, 'additionalName'),
                id_orcid=orcid,
                id_email=get(contributor, 'email'),

                # Which document they come from
                source=result['shareProperties']['source'],
                docID=result.meta.id,
                provider_updated_date_time=result['providerUpdatedDateTime']
            )

        if count % 1000 == 0:
            logger.info('Last updated datetime: {}'.format(result['providerUpdatedDateTime']))
