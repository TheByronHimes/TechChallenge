from django.shortcuts import render
from django.core.exceptions import ValidationError
from rest_framework import status as rs
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PcrTest, validateToken, validateDateStringFormat
from .support import generateToken, sampleID


def error():
    """ Produces generic error response """
    return {'msg': 'Internal error occurred'}, rs.HTTP_500_INTERNAL_SERVER_ERROR


def enumErrors(e):
    """ This returns a dict with validation errors for display """
    errList = '\n'.join([err[1][0] for err in e])
    return {'msg': errList}


@api_view(['GET', 'POST', 'PATCH'])
def sample(request, parm=''):

    # Handle GET req and return test sample information if found
    if request.method=='GET':
        access_token = parm.strip()
        data_to_return, status_code = findSample(access_token)

        return Response(data_to_return, status=status_code)

    # Handle POST req, insert new data, and return sample_id and access_token
    elif request.method=='POST':
        req = request.data
        data_to_return, status_code = addSample(
            req['patient_pseudonym'],
            req['submitter_email'],
            req['collection_date']
        )

        return Response(data_to_return, status_code)

    # Hand PATCH req, find sample with matching access_token and update
    elif request.method=='PATCH':
        req = request.data
        data_to_return, status_code = updateSample(
            req['access_token'],
            req['status'],
            req['test_result'],
            req['test_date']
        )

        return Response(data_to_return, status=status_code)


def addSample(patient_pseudonym, submitter_email, collection_date):
    """ Adds a PcrTest to the database """
    try:

        sample_id = sampleID()

        # generate a 16-character access token
        access_token = generateToken(16)

        # Attempt to add the sample
        p = PcrTest(
            sample_id=sample_id,
            patient_pseudonym=patient_pseudonym,
            submitter_email=submitter_email,
            collection_date=collection_date,
            access_token=access_token,
            status='',
            test_result='',
            test_date=''
        )

        # run custom validators and save
        try:
            p.full_clean()
            p.save()
        except ValidationError as e:
            return enumErrors(e), rs.HTTP_400_BAD_REQUEST

        data_to_return = {
            'sample_id': sample_id,
            'access_token': access_token
        }

        return data_to_return, rs.HTTP_201_CREATED
    except:
        return error()


def findSample(access_token):
    """ Looks for a PcrTest object with matching access_token """
    try:
        data_to_return = {'msg': 'sample for %s not found' % access_token}
        code = rs.HTTP_404_NOT_FOUND

        try:
            # Validate access token
            validateToken(access_token)
        except ValidationError as e:
            return enumErrors(e), rs.HTTP_400_BAD_REQUEST

        # access token was good, perform search
        p = PcrTest.objects.filter(access_token=access_token)
        if p.exists():
            data_to_return = {
                'patient_pseudonym': p[0].patient_pseudonym,
                'submitter_email': p[0].submitter_email,
                'collection_date': p[0].collection_date,
                'status': p[0].status,
                'test_result': p[0].test_result,
                'test_date': p[0].test_date
            }
            code = rs.HTTP_200_OK

        return data_to_return, code
    except:
        return error()


def index(request, path='COVID Test Portal'):
    """ The only function that gets called by paths matching react routes """
    return render(request, 'ghga/index.html', {'title':path.title()})


def updateSample(access_token, status, test_result, test_date):
    """ Updates a sample with test results """
    try:
        # start with default msg and code
        msg = 'Update was successful.'
        code = rs.HTTP_200_OK

        try:
            # validate token and date parameters
            validateToken(access_token)
            validateDateStringFormat(test_date)
        except ValidationError as e:
            return enumErrors(e), rs.HTTP_400_BAD_REQUEST

        # validate status and test_result since they're connected
        bad_parms = False
        if status not in ['', 'completed', 'failed'] or\
        test_result not in ['', 'positive', 'negative']:
            bad_parms = True
            msg = 'Status or test_result was invalid.'
        elif status in ('', 'failed'):
            if test_result != '':
                bad_parms = True
                msg = 'Invalid combination of status and test result.'
        elif status == 'completed':
            if test_result == '':
                bad_parms = True
                msg = 'Invalid combination of status and test result.'
        if bad_parms:
            return {'msg': msg}, rs.HTTP_400_BAD_REQUEST


        p = PcrTest.objects.filter(
            access_token=access_token
        )

        if p.exists():
            p = p[0]
            p.status = status
            p.test_result = test_result
            p.test_date = test_date
            p.save()
        else:
            msg = 'No record found with that token.'
            code = rs.HTTP_404_NOT_FOUND

        return {'msg': msg}, code
    except:
        return error()



