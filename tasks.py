import os
from invoke import task

from enshance.tasks import gather_contributors, gather_email_orcid, gather_email_from_orcid


@task
def get_email_orcid(start=None, async=False):
    from enshance import settings
    settings.CELERY_ALWAYS_EAGER = not async
    gather_email_orcid(start).delay()


@task
def get_email_from_orcid(start=None, async=False):
    from enshance import settings
    settings.CELERY_ALWAYS_EAGER = not async
    gather_email_from_orcid(start).delay()


@task
def get_contributors(start=None):
    gather_contributors(start)


@task
def reset_all():
    if raw_input('Are you sure? y/N ') != 'y':
        return
    os.system('psql -c "DROP DATABASE enshance;"')
    os.system('psql -c "CREATE DATABASE enshance;"')
    os.system('python manage.py migrate')
