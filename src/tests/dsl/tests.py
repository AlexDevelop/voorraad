import requests
import xmltodict
from django.test import TestCase

from django.conf import settings

from dsl.views import DslOrder, SingleDsl, clean_params
from utils.general import Ddict
import vcr
import os
import re
import urllib

my_vcr = vcr.VCR()  # ignore_localhost=True)


class DslTest(TestCase):
    def setUp(self):
        items = [
            Ddict(
                postcode='1319CS',
                housenumber='105',
                housenumber_add=None,
            ),
            Ddict(
                postcode='1321HS',
                housenumber='44',
                housenumber_add=None,
            ),
            Ddict(
                postcode='3603AZ',
                housenumber='14',
                housenumber_add=None,
            ),
            Ddict(
                postcode='1967DC',
                housenumber='2260',
                housenumber_add=None,
            ),
            Ddict(
                postcode='3438LE',
                housenumber='136',
                housenumber_add=None,
            ),
            Ddict(
                postcode='1716KE',
                housenumber='38',
                housenumber_add=None,
            ),
            Ddict(
                postcode='1043EJ',
                housenumber='121',
                housenumber_add=None,
            ),
            Ddict(
                postcode='1311XB',
                housenumber='6',
                housenumber_add=None,
            ),
            Ddict(
                postcode='5061KK',
                housenumber='7',
                housenumber_add=None,
            ),
        ]

        items_with_errors = [
            Ddict(
                postcode='1757PK',
                housenumber='34',
                housenumber_add='H-089',
            ),
        ]

        items_copperconnection = [
            Ddict(
                postcode='1311XB',
                housenumber='6',
                housenumber_add='',
                total_aderparen=30
            ),
            Ddict(
                postcode='1319CS',
                housenumber='105',
                housenumber_add='',
                total_aderparen=1
            ),
            Ddict(
                postcode='5061KK',
                housenumber='7',
                housenumber_add=None,
                total_aderparen=8
            ),
            Ddict(
                postcode='2542AC',
                housenumber='71',
                housenumber_add=None,
                total_aderparen=1
            ),
            Ddict(
                postcode='5025RD',
                housenumber='3',
                housenumber_add=None,
                total_aderparen=6
            ),
        ]

        items_possible_house_number_addtions = [
            Ddict(
                postcode='1332AW',
                housenumber='46',
                housenumber_add='',
                possible_house_number_additions=23
            ),
        ]

        self.items = items
        self.items_with_errors = items_with_errors
        self.items_copperconnection = items_copperconnection
        self.items_possible_house_number_addtions = items_possible_house_number_addtions

        response_v7 = requests.get('https://pqcc.soap.dslorder.nl/pqcc/v7.0/pqcc.aspx')
        self.event_validation_v7 = urllib.quote(
            re.findall('__EVENTVALIDATION.*?value=\"(.*?)\"', response_v7.content)[0], safe='')
        self.view_state_v7 = urllib.quote(re.findall('__VIEWSTATE\".*?value=\"(.*?)\"', response_v7.content)[0],
                                          safe='')

        response_v8 = requests.get('https://pqcc.soap.dslorder.nl/pqcc/v8.0/pqcc.aspx')
        self.event_validation_v8 = urllib.quote(
            re.findall('__EVENTVALIDATION.*?value=\"(.*?)\"', response_v8.content)[0], safe='')
        self.view_state_v8 = urllib.quote(re.findall('__VIEWSTATE\".*?value=\"(.*?)\"', response_v8.content)[0],
                                          safe='')

    def test_valid_dslorder_v7(self):
        with my_vcr.use_cassette(os.path.join(settings.REPOSITORY_ROOT, 'fixtures/dsl/test_valid_dslorder_v7.yaml'),
                              record_mode='new_episodes'):
            for item in self.items:
                response = DslOrder(event_validation=self.event_validation_v7,
                                    view_state=self.view_state_v7).get_dslorder_v7(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)
                data = xmltodict.parse(response.content)
                data_cleaned = clean_params(data)
                assert response.status_code is 200
                assert data_cleaned['PqccResponse']['Errors'] is None
                assert data_cleaned['PqccResponse']['Address']['PostalCode'] == item.postcode
                assert data_cleaned['PqccResponse']['Address']['HouseNumber'] == item.housenumber
                assert 'PossibleHouseNumberAdditions' in data_cleaned['PqccResponse']['Address']

    def test_valid_dslorder_v7_with_errors(self):
        with my_vcr.use_cassette(
                os.path.join(settings.REPOSITORY_ROOT, 'fixtures/dsl/test_valid_dslorder_v7_with_errors.yaml'),
                record_mode='new_episodes'):
            for item in self.items_with_errors:
                response = DslOrder(event_validation=self.event_validation_v7,
                                    view_state=self.view_state_v7).get_dslorder_v7(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)
                data = xmltodict.parse(response.content)
                data_cleaned = clean_params(data)
                assert response.status_code is 200

                assert 'EnumName' in data_cleaned['PqccResponse']['Errors']['Error'][0]
                assert 'DescriptionNed' in data_cleaned['PqccResponse']['Errors']['Error'][0]

                assert data_cleaned['PqccResponse']['Address']['PostalCode'] == item.postcode
                assert data_cleaned['PqccResponse']['Address']['HouseNumber'] == item.housenumber
                assert 'PossibleHouseNumberAdditions' in data_cleaned['PqccResponse']['Address']

    def test_valid_dslorder_v8(self):
        with my_vcr.use_cassette(os.path.join(settings.REPOSITORY_ROOT, 'fixtures/dsl/test_valid_dslorder_v8.yaml'),
                              record_mode='new_episodes'):
            for item in self.items:
                response = DslOrder(event_validation=self.event_validation_v8,
                                    view_state=self.view_state_v8).get_dslorder_v8(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)
                data = xmltodict.parse(response.content)
                data_cleaned = clean_params(data)
                assert response.status_code is 200
                assert data_cleaned['PqccResponse']['Errors'] is None
                assert data_cleaned['PqccResponse']['Address']['PostalCode'] == item.postcode
                assert data_cleaned['PqccResponse']['Address']['HouseNumber'] == item.housenumber
                assert 'PossibleHouseNumberAdditions' in data_cleaned['PqccResponse']['Address']

                housenumber_add = item.housenumber_add if item.housenumber_add else ''
                parameters = {'postcode': item.postcode, 'housenumber': item.housenumber,
                              'housenumber_add': housenumber_add}
                p = urllib.urlencode(parameters)
                response = requests.get('http://0.0.0.0:5555/dsl-info?{}'.format(p)).json()

                assert response['PostalCode'] == item.postcode
                assert response['HouseNumber'] == item.housenumber
                assert response['v8'] != None

    def test_valid_dslorder_v8_with_errors(self):
        with my_vcr.use_cassette(
                os.path.join(settings.REPOSITORY_ROOT, 'fixtures/dsl/test_valid_dslorder_v8_with_errors.yaml'),
                record_mode='new_episodes'):
            for item in self.items_with_errors:
                response = DslOrder(event_validation=self.event_validation_v8,
                                    view_state=self.view_state_v8).get_dslorder_v8(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)
                data = xmltodict.parse(response.content)
                data_cleaned = clean_params(data)
                assert response.status_code is 200

                assert 'EnumName' in data_cleaned['PqccResponse']['Errors']['Error'][0]
                assert 'DescriptionNed' in data_cleaned['PqccResponse']['Errors']['Error'][0]

                assert data_cleaned['PqccResponse']['Address']['PostalCode'] == item.postcode
                assert data_cleaned['PqccResponse']['Address']['HouseNumber'] == item.housenumber
                assert 'PossibleHouseNumberAdditions' in data_cleaned['PqccResponse']['Address']

    def test_aderparen_v7(self):
        with my_vcr.use_cassette(os.path.join(settings.REPOSITORY_ROOT,
                                           'fixtures/dsl/test_aderparen_{}.yaml'.format(self.get_version_number()))):
            for item in self.items_copperconnection:
                response = DslOrder(event_validation=self.event_validation_v7,
                                    view_state=self.view_state_v8).get_dslorder_v7(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)

                assert response.status_code is 200

    def test_aderparen_v8(self):
        with my_vcr.use_cassette(os.path.join(settings.REPOSITORY_ROOT,
                                           'fixtures/dsl/test_aderparen_{}.yaml'.format(self.get_version_number())),):
            for item in self.items_copperconnection:
                response = DslOrder(event_validation=self.event_validation_v8,
                                    view_state=self.view_state_v8).get_dslorder_v8(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)
                assert response.status_code is 200

                housenumber_add = item.housenumber_add if item.housenumber_add else ''
                parameters = {'postcode': item.postcode, 'housenumber': item.housenumber,
                              'housenumber_add': housenumber_add}
                response = requests.get('http://0.0.0.0:5555/dsl-info', params=parameters).json()

                assert response['v8']['total_aderparen'] == item.total_aderparen

    def test_possible_house_number_additions_v8(self):
        with my_vcr.use_cassette(os.path.join(settings.REPOSITORY_ROOT,
                                           'fixtures/dsl/test_possible_house_number_additions_{}.yaml'.format(self.get_version_number())),):
            for item in self.items_possible_house_number_addtions:
                response = DslOrder(event_validation=self.event_validation_v8,
                                    view_state=self.view_state_v8).get_dslorder_v8(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)
                assert response.status_code is 200

                housenumber_add = item.housenumber_add if item.housenumber_add else ''
                parameters = {'postcode': item.postcode, 'housenumber': item.housenumber,
                              'housenumber_add': housenumber_add}
                response = requests.get('http://0.0.0.0:5555/dsl-info', params=parameters).json()

                assert len(response['v8']['possible_house_number_additions']) == item.possible_house_number_additions

    def get_version_number(self):
        return self.__name__.split('_')[-1]

    def test_backend_unavailable_v7(self):
        with my_vcr.use_cassette(os.path.join(settings.REPOSITORY_ROOT,
                                              'fixtures/dsl/test_backend_unavailable_{}.yaml'.format(
                                                  self.get_version_number())), record_mode='new_episodes'):

            for item in self.items:
                response = DslOrder(event_validation=self.event_validation_v7,
                                    view_state=self.view_state_v7).get_dslorder_v7(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)
                assert response.status_code == 500

                housenumber_add = item.housenumber_add if item.housenumber_add else ''
                parameters = {'postcode': item.postcode, 'housenumber': item.housenumber,
                              'housenumber_add': housenumber_add}
                response = requests.get('http://0.0.0.0:7777/dsl-info', params=parameters)
                assert response.status_code == 200

                content = response.json()
                assert "Something went wrong - V7: 500 - V8: 500" in content

                # TODO Check frontend for content too

    def test_backend_unavailable_v8(self):
        with my_vcr.use_cassette(os.path.join(settings.REPOSITORY_ROOT,
                                              'fixtures/dsl/test_backend_unavailable_{}.yaml'.format(
                                                  self.get_version_number())), record_mode='new_episodes'):
            for item in self.items:
                response = DslOrder(event_validation=self.event_validation_v8,
                                    view_state=self.view_state_v8).get_dslorder_v8(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)
                assert response.status_code == 500

                housenumber_add = item.housenumber_add if item.housenumber_add else ''
                parameters = {'postcode': item.postcode, 'housenumber': item.housenumber,
                              'housenumber_add': housenumber_add}
                response = requests.get('http://0.0.0.0:7777/dsl-info', params=parameters)
                assert response.status_code == 200

                content = response.json()
                assert "Something went wrong - V7: 500 - V8: 500" in content

                # TODO Check frontend for content too

    def test_possible_additions_v7(self):
        with my_vcr.use_cassette(os.path.join(settings.REPOSITORY_ROOT,
                                              'fixtures/dsl/test_possible_additions_{}.yaml'.format(
                                                  self.get_version_number())), record_mode='new_episodes'):
            for item in self.items:
                response = DslOrder(event_validation=self.event_validation_v7,
                                    view_state=self.view_state_v7).get_dslorder_v7(item.postcode, item.housenumber,
                                                                                   item.housenumber_add)

                assert response.status_code == 200

                housenumber_add = item.housenumber_add if item.housenumber_add else ''
                parameters = {'postcode': item.postcode, 'housenumber': item.housenumber,
                              'housenumber_add': housenumber_add}
                response = requests.get('http://0.0.0.0:7777/dsl-info', params=parameters)
                assert response.status_code == 200

                content = response.json()

                if item.postcode == '1321HS' and item.housenumber == '44':
                    assert content['additions_v7'][0] == 'LFT'

                if item.postcode == '1716KE' and item.housenumber == '38':
                    assert content['additions_v7'][0] == 'BETO'
                    assert content['additions_v7'][1] == 'CLUB'