import secrets
import string
from django.db.models import Max
from .models import PcrTest

def generateToken(length=16):
    """ Generates an alphanumeric of length 'length' using secrets """

    seq = string.ascii_lowercase + string.digits
    token = ''.join([secrets.choice(seq) for x in range(length)])

    return token


def sampleID():
    return (PcrTest.objects.aggregate(\
        Max('sample_id'))['sample_id__max'] or 0) + 1
