# Python SDK for CloudCIX API #

An Python SDK implementation to make the work with CloudCIX API fun.

# Installation #

You should install the requirements from pip-requires before your start working
with the SDK. 

# Required settings #

When you run your project you should set the settings variable 
`CLOUDCIX_SETTINGS_MODULE` to point to the module that contains all the 
necessary settings.

Example when used with django (in manage.py add): 


    import os
    os.environ['CLOUDCIX_SETTINGS_MODULE'] = 'django.conf.settings'

Required `CLOUDCIX` and `OPENSTACK` settings


    CLOUDCIX_SERVER_URL = 'https://api.cloudcix.com'
    CLOUDCIX_API_USERNAME = 'user@cloudcix.com'
    CLOUDCIX_API_PASSWORD = 'super53cr3t3'
    CLOUDCIX_API_ID_MEMBER = 2243
    OPENSTACK_KEYSTONE_URL = 'http://keystone.cloudcix.com:5000/v3'

# Sample usage #

## Use the language service ##


    from cloudcix_sdk import api
    from cloudcix_sdk.utils import get_admin_session
    
    # get an admin token
    token = get_admin_session().get_token()
    
    # call a sample membership service
    api.membership.language.list()
    
## Create token for a User, and read the User Address ##


    from cloudcix_sdk import api
    from cloudcix_sdk.cloudcixauth import CloudCIXAuth
    from cloudcix_sdk.utils import KeystoneSession, KeystoneClient, \
        get_admin_client
    from keystoneclient.exceptions import NotFound

    # create auth payload
    auth = CloudCIXAuth(
        auth_url=settings.OPENSTACK_KEYSTONE_URL,
        username='john@doe.com',
        password='ubersecret',
        idMember=2243)
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

    # check the response status to ensure we've been able to read the address
    if response.status_code != 200:
        # we couldn't read the address
        return response.content

    address = response.json()['content']

    # Finally delete the token
    admin_cli.tokens.revoke_token(user_token)

    # And make sure it's not longer valid
    try:
        admin_cli.tokens.validate(user_token)
    except NotFound as e:
        # Token is not longer valid
        pass

## Given an expiring token, get a new token for further calls ##


    from cloudcix_sdk.utils import KeystoneTokenAuth, KeystoneSession
    
    expiring_token = 'xyz123'
    auth = KeystoneTokenAuth(
        auth_url=settings.OPENSTACK_KEYSTONE_URL,
        token=expiring_token)
    new_token = KeystoneSession(auth=auth).get_token()