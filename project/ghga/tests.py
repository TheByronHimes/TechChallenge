import re
from unittest import expectedFailure
from django.test import TestCase
from .models import PcrTest
from .support import generateToken, sampleID
from . import views


class SupportModuleTests(TestCase):

    @expectedFailure
    def test_generateToken_with_invalid_parm(self):
        generateToken('fail_this_test')
        print('Allowed invalid parameter in generateToken()')
        self.assertIs(True, True)

    def test_generateToken_without_parm(self):
        x = generateToken()
        ms = re.compile(r'^[0-9a-z]{16}$')
        if re.match(ms, x):
            self.assertIs(True, True)
        else:
            self.fail('generateToken() output was in unexpected format: %s' % x)

    def test_generateToken_with_valid_parm(self):
        x = generateToken(10)
        ms = re.compile(r'^[0-9a-z]{10}$')
        if re.match(ms, x):
            self.assertIs(True, True)
        else:
            self.fail('generateToken() output was in unexpected format: %s' % x)

    def test_sampleID_output(self):
        x = sampleID()
        self.assertIs(type(x), int)


class MiscTests(TestCase):

    def test_error_func(self):
        obj, code = views.error()
        self.assertIs(True, (obj=={'msg': 'Internal error occurred'} and \
            code==500))


class AddSampleTests(TestCase):

    def test_addSample_func_good(self):
        d, code = views.addSample(
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18'
        )

        exp_keys = {'sample_id', 'access_token'}
        exp_code = 201

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_addSample_name_too_long(self):
        d, code = views.addSample(
            patient_pseudonym = ''.join(['a' for i in range(65)]),
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18'
        )

        exp_keys = {'msg'}
        exp_code = 400

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_addSample_name_too_short(self):
        d, code = views.addSample(
            patient_pseudonym = '0123456789',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18'
        )

        exp_keys = {'msg'}
        exp_code = 400

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_addSample_email_too_long(self):
        d, code = views.addSample(
            patient_pseudonym = 'Alfred Hitchcock',
            submitter_email = 'testtesttesttesttesttesttesttesttesttesttesttest\
            testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttest\
            testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttest\
            testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttest\
            testtesttest@test.com',
            collection_date = '2022-08-21T11:18'
        )

        exp_keys = {'msg'}
        exp_code = 400

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_addSample_email_invalid1(self):
        d, code = views.addSample(
            patient_pseudonym = 'Alfred Hitchcock',
            submitter_email = 'testtest.com',
            collection_date = '2022-08-21T11:18'
        )

        exp_keys = {'msg'}
        exp_code = 400

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_addSample_email_invalid2(self):
        d, code = views.addSample(
            patient_pseudonym = 'Alfred Hitchcock',
            submitter_email = 'test@test',
            collection_date = '2022-08-21T11:18'
        )

        exp_keys = {'msg'}
        exp_code = 400

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_addSample_email_invalid3(self):
        d, code = views.addSample(
            patient_pseudonym = 'Alfred Hitchcock',
            submitter_email = 'test.test.test@test.com',
            collection_date = '2022-08-21T11:18'
        )

        exp_keys = {'msg'}
        exp_code = 400

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))


class FindSampleTests(TestCase):

    def test_find_existing_sample(self):
        # create object
        at = '12345678abcdefgh'
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'good test result',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token = at
        )
        p.save()

        d, code = views.findSample(at)
        exp_code = 200
        exp_keys = {
            'patient_pseudonym',
            'submitter_email',
            'collection_date',
            'status',
            'test_result',
            'test_date'
        }

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_find_nonexistent_sample(self):
        # there is a practically 0% chance that this token will be in use.
        d, code = views.findSample('aaaaaaaaaaaaaaqz')
        exp_code = 404
        exp_keys = {'msg'}

        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_find_with_bad_token_not_empty(self):
        d, code = views.findSample('1')
        exp_code = 400
        exp_keys = {'msg'}
        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_find_with_bad_token_empty(self):
        d, code = views.findSample('1')
        exp_code = 400
        exp_keys = {'msg'}
        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))


class UpdateSampleTests(TestCase):

    def test_update_completed_positive(self):
        at = 'thisisntokayisit'
        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token = at
        )
        p.save()

        d, code = views.updateSample(
            access_token = at,
            status = 'completed',
            test_result = 'positive',
            test_date = '2022-08-21T11:18'
        )

        exp_code = 200
        exp_keys = {'msg'}
        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_update_failed_no_result(self):
        at = 'thisisntokaynum2'
        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token = at
        )
        p.save()

        d, code = views.updateSample(
            access_token = at,
            status = 'failed',
            test_result = '',
            test_date = '2022-08-21T11:18'
        )

        exp_code = 200
        exp_keys = {'msg'}
        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_update_no_status_negative(self):
        at = 'thisisntokaynum3'
        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token = at
        )
        p.save()

        d, code = views.updateSample(
            access_token = at,
            status = '',
            test_result = 'negative',
            test_date = '2022-08-21T11:18'
        )

        exp_code = 400
        exp_keys = {'msg'}
        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_update_completed_no_result(self):
        at = 'thisisntokaynum4'
        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token = at
        )
        p.save()

        d, code = views.updateSample(
            access_token = at,
            status = 'completed',
            test_result = '',
            test_date = '2022-08-21T11:18'
        )

        exp_code = 400
        exp_keys = {'msg'}
        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))

    def test_update_nonexistent_record(self):
        d, code = views.updateSample(
            access_token = 'aaaaaaaaaaaaaaqz',
            status = 'failed',
            test_result = '',
            test_date = '2022-08-21T11:18'
        )

        exp_code = 404
        exp_keys = {'msg'}
        self.assertIs(True, (d.keys() == exp_keys and code == exp_code))


class PcrTestModelTests(TestCase):

    def test_with_all_valid_input(self):
        """ Uses valid input to add an object """
        try:
            # create object
            p = PcrTest(
                sample_id = sampleID(),
                patient_pseudonym = 'Alfredo Barnelli',
                submitter_email = 'test@test.com',
                collection_date = '2022-08-21T11:18',
                access_token = '1234567812345678'
            )
            p.save()
            self.assertIs(True, True)
        except:
            self.fail('Failed to create PcrTest with valid data!')

    @expectedFailure
    def test_with_too_long_name(self):

        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'sadfasdfasdfasdasdfkjalsdkjflaks\
                djlfkasdlkfasldkfjalksdjfsdfdfdd',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token = '2234567812345678'
        )
        p.full_clean()
        p.save()

        print('PcrTest was created with too-long string for name')
        self.assertIs(True, True)

    @expectedFailure
    def test_with_too_short_name(self):

        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = '0123456789',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token = '3234567812345678'
        )
        p.full_clean()
        p.save()

        print('PcrTest was created with too-short string for name')
        self.assertIs(True, True)

    @expectedFailure
    def test_with_invalid_email_format(self):

        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'testtest.com',
            collection_date = '2022-08-21T11:18',
            access_token = '43234567812345678'
        )
        p.full_clean()
        p.save()

        print('PcrTest accepted invalid email address')
        self.assertIs(True, True)

    @expectedFailure
    def test_with_bad_status(self):

        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            status='invalid',
            access_token = '53234567812345678'
        )
        p.full_clean()
        p.save()

        print('invalid status was accepted')
        self.assertIs(True, True)

    @expectedFailure
    def test_with_too_long_email(self):

        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'testtesttesttesttesttesttesttesttesttesttesttest\
            testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttest\
            testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttest\
            testtesttesttesttesttesttesttesttesttesttesttesttesttesttesttest\
            testtesttest@test.com',
            collection_date = '2022-08-21T11:18',
            access_token = '63234567812345678'
        )
        p.full_clean()
        p.save()

        print('PcrTest accepted too-long email address')
        self.assertIs(True, True)

    @expectedFailure
    def test_with_too_long_token(self):

        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token='a1b2c3d4e5f6g7h8i9'
        )
        p.full_clean()
        p.save()

        print('PcrTest accepted too-long access_token')
        self.assertIs(True, True)

    @expectedFailure
    def test_with_invalid_token(self):

        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18',
            access_token='a1b2c3d4e5f6g7h$'
        )
        p.full_clean()
        p.save()

        print('PcrTest accepted invalid access_token')
        self.assertIs(True, True)

    @expectedFailure
    def test_with_date_no_T(self):
        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21 11:18',
            access_token = '73234567812345678'
        )
        p.full_clean()
        p.save()

    @expectedFailure
    def test_with_date_short_year(self):
        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '22-08-21T11:18',
            access_token = '83234567812345678'
        )
        p.full_clean()
        p.save()

    @expectedFailure
    def test_with_date_with_milliseconds(self):
        # create object
        p = PcrTest(
            sample_id = sampleID(),
            patient_pseudonym = 'Alfredo Barnelli',
            submitter_email = 'test@test.com',
            collection_date = '2022-08-21T11:18.357',
            access_token = '93234567812345678'
        )
        p.full_clean()
        p.save()


