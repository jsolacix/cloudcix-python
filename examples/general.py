"""
###############################################################################
# Using the SDK                                                               #
###############################################################################

To use the SDK you should be be able to import it from your Python PATH.
"""
import os
# If you are using the SDK from your project you should set an environment
# variable that will be used to import any necessary settings, for example in
# django you would
os.environ['CLOUDCIX_SETTINGS_MODULE'] = 'django.conf.settings'

# If you are using the Python console it is enough to set the
# CLOUDCIX_SERVER_URL as environment variable
os.environ['CLOUDCIX_SERVER_URL'] = 'https://api.cloudcix.com/'

# utils method get_admin_token and get_admin_session, will require you to set
# following environment variables as well
os.environ['CLOUDCIX_API_USERNAME'] = 'user@cloudcix.com'
os.environ['CLOUDCIX_API_PASSWORD'] = 'super53cr3t3'
os.environ['CLOUDCIX_API_ID_MEMBER'] = 2243
os.environ['OPENSTACK_KEYSTONE_URL'] = 'https://keystone.cloudcix.com:5000/v3'

###############################################################################
# Use Keystone to get a token.                                                #
###############################################################################
from cloudcix import api
from cloudcix.cloudcixauth import CloudCIXAuth, KeystoneTokenAuth
from cloudcix.utils import KeystoneSession, KeystoneClient


auth = CloudCIXAuth(
    auth_url='https://keystone.cloudcix.com:5000/v3',
    username='john@doe.com',
    password='secrete',
    idMember=4332)
auth_session = KeystoneSession(auth=auth)

auth_session.get_token()
# after we call the .get_token method, token data becomes available as the
# auth_ref parameter of our session.auth

# let's store token data for later use
token_data = auth_session.auth.auth_ref

###############################################################################
# Use the existing token to create a new token (in case when current is about #
# to expire)                                                                  #
###############################################################################

auth = KeystoneTokenAuth(
    auth_url='https://keystone.cloudcix.com:5000/v3',
    token=auth_session.get_token()
)
new_session = KeystoneSession(auth=auth)
new_token = new_session.get_token()


###############################################################################
# Use membership to list users in your address                                #
###############################################################################

# create query filters that will limit the results only to the users in your
# address
params = {
    'idAddress': token_data['user']['idAddress']
}
response = api.membership.user.list(token=token_data['auth_token'],
                                    params=params)

# check that the call was successful
if response.status_code != 200:
    assert False, "we've got a problem"

# do something with users
address_users = response.json()['content']


###############################################################################
# Use membership to create a new user in your address                         #
###############################################################################

idAddress = token_data['user']['idAddress']
user_data = {
    'username': 'john2@doe.com',
    'idAddress': idAddress,
    'password': 'asff4f4s',
    'idLanguage': 1,
    'firstName': 'John',
    'surname': 'Doe',
    'timezone': 'Europe/Dublin',
    'startDate': '2015-02-01',
    'expiryDate': '2016-02-01'
}
response = api.membership.user.create(token=token_data['auth_token'],
                                      data=user_data)

# check that the call was successful
if response.status_code != 201:
    assert False, "we've got a problem"

new_user_id = response.json()['content']['idUser']

###############################################################################
# Use membership to read the user                                             #
###############################################################################


response = api.membership.user.read(token=token_data['auth_token'],
                                    pk=new_user_id)

# check that the response was successful
if response.status_code != 200:
    assert False, "we've got a problem"

user_obj = response.json()['content']  # do something with the user object

###############################################################################
# Use keystone to delete a token                                              #
###############################################################################

# Let's use our existing session and delete our token
# For that we'll need to tie our session to keystoneclient. While doing that
# we need to tell keystone client where exactly it should direct it's call by
# specifying endpoint_override argument
keystone_uri = 'https://keystone.cloudcix.com:5000/v3/'
keystone_cli = KeystoneClient(session=auth_session, auth_url=keystone_uri,
                              endpoint_override=keystone_uri)

# Now we can use the client to delete the token
keystone_cli.tokens.revoke_token(token_data['auth_token'])

# with our own token deleted we won't be able to use it
keystone_cli.tokens.validate(token_data['auth_token'])
