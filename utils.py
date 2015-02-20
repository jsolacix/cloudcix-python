# python
from __future__ import unicode_literals
import importlib
import os

# libs
from keystoneclient.session import Session as KeystoneSession
from keystoneclient.v3.client import Client as KeystoneClient

# local
from .cloudcixauth import CloudCIXAuth

__all__ = ['KeystoneSession', 'KeystoneClient', 'settings',
           'get_admin_session', 'get_admin_client']


def new_method_proxy(func):
    """When attribute is accessed in lazy object, this method makes sure that
    lazy object was properly initialized and _setup method has been run
    """
    def inner(self, *args):
        if self._wrapped is None:
            self._setup()
        return func(self._wrapped, *args)
    return inner


class LazySettings(object):
    """Lazy settings module. We want settings to be imported when they are
    accessed not earlier.
    """
    _wrapped = None
    __getattr__ = new_method_proxy(getattr)

    def _setup(self):
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time we need any settings at all, if the user has not
        previously configured the settings manually.
        """
        try:
            settings_module = os.environ['CLOUDCIX_SETTINGS_MODULE']
            if not settings_module:  # If it's set but is an empty string.
                raise KeyError
        except KeyError:
            raise ImportError("You must specify the CLOUDCIX_SETTINGS_MODULE "
                              "environment variable.")
        else:
            self._wrapped = importlib.import_module(settings_module)


settings = LazySettings()


def get_admin_session():
    t = CloudCIXAuth(
        auth_url=settings.OPENSTACK_KEYSTONE_URL,
        username=settings.CLOUDCIX_API_USERNAME,
        password=settings.CLOUDCIX_API_PASSWORD,
        idMember=settings.CLOUDCIX_API_ID_MEMBER,
        scope={'domain': {'id': settings.CLOUDCIX_API_ID_MEMBER}})
    admin_session = KeystoneSession(auth=t)
    admin_session.get_token()
    return admin_session


def get_admin_client():
    admin_session = get_admin_session()
    return KeystoneClient(session=admin_session,
                          auth_url=settings.OPENSTACK_KEYSTONE_URL,
                          endpoint_override=settings.OPENSTACK_KEYSTONE_URL)
