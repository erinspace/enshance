#  Celery tasks for enshance
from __future__ import unicode_literals

import os
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
    try:
        return d[key]
    except KeyError:
        return default


def debug(func):
    def inner(*args, **kwargs):
        import ipdb
        with ipdb.launch_ipdb_on_exception():
            return func(*args, **kwargs)
    return inner


def start_email_orcid():
    all_people = GatheredContributor.objects.all()

    for person in all_people:
        if person.email:
            query_orcid_one_email(person.id, person.email).delay()
        if person.id_orcid:
            query_orcid_one_id(person.id, person.id_orcid)


@app.task(rate_limit=1)
def query_orcid_one_email(db_id, email):
    email_search_url = ORCID_BASE_URL + 'email:{}'.format(email)

    orcid_data = requests.get(email_search_url, headers={'Accept': 'application/orcid+json'}).json()
    if orcid_data['orcid-search-results']['num-found'] == 1:
        contributor = GatheredContributor.objects.get(id=db_id)

        contributor.id_orcid = orcid_data['orcid-search-results']['orcid-search-result'][0]['orcid-profile']['orcid-identifier']['uri']
        contributor.raw_orcid = orcid_data['orcid-search-results']['orcid-search-result']
        contributor.save()


@app.task(rate_limit=1)
def query_orcid_one_id(db_id, orcid):
    orcid_search_url = ORCID_BASE_URL + 'orcid:{}'.format(orcid)

    orcid_data = requests.get(orcid_search_url, headers={'Accept': 'application/orcid+json'}).json()
    if orcid_data['orcid-search-results']['num-found'] == 1:
        contributor = GatheredContributor.objects.get(id=db_id)

        all_emails = orcid_data['orcid-search-results']['orcid-search-result'][0]['orcid-profile']['orcid-bio']['contact-details']['email']
        email = None
        for email in all_emails:
            if email['current']:
                email = email['value']
        contributor.email = email
        contributor.save()


@app.task
@debug
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
