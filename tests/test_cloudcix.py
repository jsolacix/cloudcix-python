# python
from __future__ import unicode_literals
import os
import sys
import unittest

# libs

# test imports

ROOT = lambda base: os.path.abspath(os.path.join(
    os.path.dirname(__file__), base).replace('\\', '/'))
sys.path.insert(0, ROOT('../'))

os.environ['CLOUDCIX_SETTINGS_MODULE'] = 'cloudcix.settings_local'
from cloudcix import api
from cloudcix.utils import (get_admin_session, get_admin_client, settings,
    KeystoneSession)
from cloudcix.cloudcixauth import CloudCIXAuth, KeystoneTokenAuth
from keystoneclient.exceptions import NotFound


class TestAPIUseCases(unittest.TestCase):

    def setUp(self):
        self.assertTrue(settings.CLOUDCIX_SERVER_URL, 'Test cases expect that '
                        'you create settings_local.py with required values.'
                        'See README for list of required OPENSTACK and '
                        'CLOUDCIX variables.')

    def test_basic_use_case(self):
        """basic_use_case

        1) Get an admin token
        2) read the language service
        """
        token = get_admin_session().get_token()
        self.assertTrue(token)
        response = api.membership.language.list(token=token)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()['content']), 0)

    def test_user_token(self):
        """
        1) Get a token for a user
        2) using admin session ensure the token is valid
        3) read user's address
        4) dispose of the token"""
        # create auth payload
        auth = CloudCIXAuth(
            auth_url=settings.OPENSTACK_KEYSTONE_URL,
            username=settings.CLOUDCIX_API_USERNAME,
            password=settings.CLOUDCIX_API_PASSWORD)
        auth_session = KeystoneSession(auth=auth)
        user_token = auth_session.get_token()
        token_data = auth_session.auth.auth_ref

        # for the sake of example check that the token is valid
        # you should use your admin credentials to check user's token
        admin_cli = get_admin_client()
        try:
            admin_cli.tokens.validate(user_token)
        except NotFound as e:
            # Token is invalid, re-raise the exception
            raise e
        # token is valid, continue

        # Finally, read the address
        response = api.membership.address.read(
            pk=token_data['user']['address']['idAddress'],
            token=user_token)

        # check the response status to ensure we've been able to read the
        # address
        self.assertEqual(response.status_code, 200)

        # check the object
        self.assertTrue(response.json()['content'])

        # Finally delete the token
        admin_cli.tokens.revoke_token(user_token)
        # And make sure it's not longer valid
        try:
            admin_cli.tokens.validate(user_token)
        except NotFound as e:
            # Token is invalid pass the test
            pass

    def test_extend_token(self):
        token = get_admin_session().get_token()
        auth = KeystoneTokenAuth(
            auth_url=settings.OPENSTACK_KEYSTONE_URL,
            token=token)
        session = KeystoneSession(auth=auth)
        self.assertNotIn(session.get_token(), [token, '', None])
        self.assertTrue(session.auth.auth_ref)

if __name__ == '__main__':
    unittest.main()
