from django.db import models
from django_pgjson.fields import JsonField


class GatheredContributor(models.Model):
    # Person
    raw_name = models.TextField()  # source name we got
    name = models.TextField()  # reconstructed - given+add+fam
    family_name = models.TextField(null=True)
    given_name = models.TextField(null=True)
    additional_name = models.TextField(null=True)
    institution = models.TextField(null=True)
    id_osf = models.CharField(max_length=10, null=True)
    id_orcid = models.CharField(max_length=100, null=True)
    id_email = models.TextField(null=True)
    raw_orcid = JsonField(null=True)

    # Which document they come from
    source = models.CharField(max_length=255)
    docID = models.TextField()
    provider_updated_date_time = models.CharField(max_length=100, null=True)

    # ORCID Name fields for comparison
    orcid_given_name = models.TextField(null=True)
    orcid_family_name = models.TextField(null=True)
    orcid_additional_name = models.TextField(null=True)
    orcid_name = models.TextField(null=True)


class Response(models.Model):
    key = models.TextField(primary_key=True)

    method = models.CharField(max_length=8)
    url = models.TextField()

    # Raw request data
    ok = models.NullBooleanField(null=True)
    content = models.BinaryField(null=True)
    encoding = models.TextField(null=True)
    headers_str = models.TextField(null=True)
    status_code = models.IntegerField(null=True)
    time_made = models.DateTimeField(auto_now=True)
