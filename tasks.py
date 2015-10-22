import os
from invoke import task

from enshance.tasks import gather_contributors


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
