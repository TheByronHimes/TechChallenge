import re
from django.db import models
from django.core.exceptions import ValidationError

def validateEmailFormat(v):
    ms = re.compile(r'^[0-9a-zA-z]+\.?[0-9a-zA-z]*@[0-9a-zA-z]+\.?[0-9a-zA-z]+$')
    if not re.match(ms, v):
        raise ValidationError('Email format is not right')

def validateEmailLength(v):
    if len(v) > 254:
        raise ValidationError('Emails must be 254 chars or less.')


def validateNameLongEnough(v):
    if len(v) < 11:
        raise ValidationError('Patient pseudonym must be at least 11 chars.')


def validateNameShortEnough(v):
    if len(v) > 63:
        raise ValidationError('Patient pseudonym must be less than 64 chars.')


def validateToken(v):
    ms = re.compile(r'^[0-9a-z]{16}$')
    if not re.match(ms, v):
        raise ValidationError('Access Tokens are 16 lower-case alphanumerics.')


def validateDateStringFormat(v):
    ms = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}[zZ]?')
    if not re.match(ms, v):
        raise ValidationError('Dates to be in YYYY-MM-DDTHH:SS format.')


# Create your models here.
class PcrTest(models.Model):

    # define the choices for the status and results fields
    COMPLETED = 'completed'
    FAILED = 'failed'

    STATUSES = [
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
    ]

    POSITIVE = 'positive'
    NEGATIVE = 'negative'

    RESULTS = [
        (POSITIVE, 'Positive'),
        (NEGATIVE, 'Negative'),
    ]


    sample_id = models.PositiveIntegerField(
        unique=True,
        verbose_name='Sample ID'
    )

    patient_pseudonym = models.CharField(
        max_length=63,
        verbose_name='Patient Pseudonym',
        validators=[validateNameLongEnough, validateNameShortEnough]
    )

    submitter_email = models.EmailField(
        verbose_name='Submitter',
        max_length=254,
        validators=[validateEmailFormat, validateEmailLength]
    )

    collection_date = models.CharField(
        blank=True,
        max_length=30,
        verbose_name='Collection Date',
        validators=[validateDateStringFormat]
    )

    access_token = models.CharField(
        primary_key=True,
        max_length=16,
        verbose_name='Access Token',
        validators=[validateToken]
    )

    status = models.CharField(
        max_length=10,
        blank=True,
        choices=STATUSES,
        verbose_name='Status'
    )

    test_result = models.CharField(
        max_length=10,
        blank=True,
        choices=RESULTS,
        verbose_name='Result'
    )

    test_date = models.CharField(
        blank=True,
        max_length=30,
        verbose_name='Test Date',
        validators=[validateDateStringFormat]
    )



