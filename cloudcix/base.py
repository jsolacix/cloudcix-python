# python
from __future__ import unicode_literals
import json
import os
import re

# libs
import requests
from requests.auth import AuthBase

# local
from .utils import settings

try:
    CLOUDCIX_SERVER_URL = getattr(settings, 'CLOUDCIX_SERVER_URL', None)
except ImportError:
    CLOUDCIX_SERVER_URL = os.environ['CLOUDCIX_SERVER_URL']


class TokenAuth(AuthBase):
    """Requests authentication object"""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['X-Auth-Token'] = self.token
        return r


class APIClient(object):

    def __init__(self, application, service_uri, server_url=None,
                 api_version='v1'):
        """Initialises the APIClient with details necessary for the call

        :param application: Application name that will be used as part of
                            service uri, eg. "Membership"
        :type application: str | unicode
        :param service_uri: Service uri part, eg. "User/"
        :type service_uri: str | unicode
        :param server_url: Optional, server url for the call,
                           eg. "http://api.cloudcix.com",
                           default: contents of the settings.CLOUCIX_SERVER_URL
                                    variable
        :type server_url: str | unicode
        :param api_version: Version of the service that should be used,
                            eg. "v1", default: "v1"
        :type api_version: str | unicode
        """
        self.application = application
        self.headers = {
            'content-type': 'application/json',
        }
        self.service_uri = service_uri
        self.server_url = server_url or self._get_server_url
        self.api_version = api_version

    def __repr__(self):
        return u'<APIClient(%s)>' % "/".join([
            self.server_url, self.application, self.api_version,
            self.service_uri])

    @property
    def _get_server_url(self):
        """Returns the CloudCIX server url.

        :returns: CloudCIX server url
        :rtype: unicode
        """
        self.server_url = CLOUDCIX_SERVER_URL.rstrip('/')
        return self.server_url

    def create(self, token=None, data=None, params=None, **kwargs):
        """Used to create a new resource.

        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param dict data: Optional, Data to be sent with the request.
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any positional arguments required but the service
                       method. For example if method is available at
                       /Membership/v1/Member/<idMember>/Territories/
                       you should pass in idMember=xxx as part of kwargs.
                       Additionally any other parameters that should be passed
                       to requests library call
        :returns: requests.Response
        """
        return self._call('post', token, data=data, params=params, **kwargs)

    def read(self, pk, token=None, params=None, **kwargs):
        """Used to retrieve existing resource.

        :param pk: Unique identifier (primary key) of the object
        :type pk: str | unicode | int
        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any positional arguments required but the service
                       method. For example if method is available at
                       /Membership/v1/Member/<idMember>/Territories/
                       you should pass in idMember=xxx as part of kwargs.
                       Additionally any other parameters that should be passed
                       to requests library call
        :returns: requests.Response
        """
        return self._call('get', token, pk, params=params, **kwargs)

    def update(self, pk, token=None, data=None, params=None, **kwargs):
        """Used to update existing resource.

        :param pk: Unique identifier (primary key) of the object
        :type pk: str | unicode | int
        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param dict data: Optional, Data to be sent with the request.
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any positional arguments required but the service
                       method. For example if method is available at
                       /Membership/v1/Member/<idMember>/Territories/
                       you should pass in idMember=xxx as part of kwargs.
                       Additionally any other parameters that should be passed
                       to requests library call
        :returns: requests.Response
        """
        return self._call('put', token, pk, data=data, params=params, **kwargs)

    def partial_update(self, pk, token=None, data=None, params=None, **kwargs):
        """Used to partially update existing resource.

        :param pk: Unique identifier (primary key) of the object
        :type pk: str | unicode | int
        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param dict data: Optional, Data to be sent with the request. Should
                          contain only the values that are to be updated.
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any positional arguments required but the service
                       method. For example if method is available at
                       /Membership/v1/Member/<idMember>/Territories/
                       you should pass in idMember=xxx as part of kwargs.
                       Additionally any other parameters that should be passed
                       to requests library call
        :returns: requests.Response
        """
        return self._call('patch', token, pk, data=data, params=params,
                          **kwargs)

    def delete(self, pk, token=None, params=None, **kwargs):
        """Used to delete an existing resource.

        :param pk: Unique identifier (primary key) of the object
        :type pk: str | unicode | int
        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any positional arguments required but the service
                       method. For example if method is available at
                       /Membership/v1/Member/<idMember>/Territories/
                       you should pass in idMember=xxx as part of kwargs.
                       Additionally any other parameters that should be passed
                       to requests library call
        :returns: requests.Response
        """
        return self._call('delete', token, pk, params=params, **kwargs)

    def bulk_delete(self, token=None, params=None, **kwargs):
        """Used to delete a part of collection. Request body should contain a
        list of elements that should be deleted

        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any positional arguments required but the service
                       method. For example if method is available at
                       /Membership/v1/Member/<idMember>/Territories/
                       you should pass in idMember=xxx as part of kwargs.
                       Additionally any other parameters that should be passed
                       to requests library call
        :returns: requests.Response
        """
        return self._call('delete', token, params=params, **kwargs)

    def list(self, token=None, params=None, **kwargs):
        """Used to list resources in a collection.

        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any positional arguments required but the service
                       method. For example if method is available at
                       /Membership/v1/Member/<idMember>/Territories/
                       you should pass in idMember=xxx as part of kwargs.
                       Additionally any other parameters that should be passed
                       to requests library call
        :returns: requests.Response
        """
        return self._call('get', token, params=params, **kwargs)

    def head(self, pk=None, token=None, params=None, **kwargs):
        """Used to check existence of a resource/collection.

        :param pk: Optional, unique identifier (primary key) of the object
                   (if the request is against a resource)
        :type pk: str | unicode | int
        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param basestring token: Optional, Token to be used for the request.
                                 Must be present if method requires
                                 authentication.
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any positional arguments required but the service
                       method. For example if method is available at
                       /Membership/v1/Member/<idMember>/Territories/
                       you should pass in idMember=xxx as part of kwargs.
                       Additionally any other parameters that should be passed
                       to requests library call
        :returns: requests.Response
        """
        return self._call('head', token, pk, params=params, **kwargs)

    def _call(self, method, token=None, pk=None, data=None, params=None,
              **kwargs):
        """Does the actual call using the requests lib.

        :param method: on of the supported http request methods
        :type method: str | unicode | int
        :param token: Optional, Token to be used for the request.
                      Must be present if method requires authentication.
        :type token: str | unicode
        :param dict data: Optional, Data to be sent with the request. Should
                          contain only the values that are to be updated.
        :param dict params: Optional, Query params to be sent along with the
                            request.
        :param kwargs: Any additional that should be passed to requests library
                       call
        :returns: requests.Response
        """
        data = data or {}
        service_kwargs, kwargs = self.filter_service_kwargs(kwargs)
        if 'headers' in kwargs:
            kwargs['headers'].updated(self.headers)
        else:
            kwargs['headers'] = self.headers
        if token:
            kwargs['auth'] = TokenAuth(token)
        uri = self.get_uri(pk, service_kwargs)
        data = json.dumps(data)
        return getattr(requests, method)(uri, data=data, params=params,
                                         **kwargs)

    def filter_service_kwargs(self, kwargs):
        """Filters out kwargs required by the service uri from general kwargs.

        :param dict kwargs: Contains all the keyword arguments received by the
                            method
        :returns: Two dictionaries:
                    service_args - contains only the arguments required in
                                   the service uri
                    kwargs - dictionary with all the service_kwargs filtered
                             out
        :rtype: (dict, dict)
        """
        pattern = re.compile(r'(?<=/\%\()(?P<match>\w+)(?=\)s/)')
        result = pattern.findall(self.service_uri)
        service_kwargs = dict((k, v) for k, v in kwargs.items() if k in result)
        kwargs = dict(filter(lambda i: i[0] not in result, kwargs.items()))
        return service_kwargs, kwargs

    def get_uri(self, pk=None, service_kwargs=None):
        """Populates the service uri with required arguments and returns the
        final uri that should be used for the call.

        :param pk: Optional unique id if the call is made to a resource
        :type pk: str | unicode | int
        :param dict service_kwargs: dict containing any other arguments
                                    (beside pk that are required by the service
                                    uri)
        :returns: Absolute uri for the requests call
        :rtype: unicode
        """
        absolute_uri = "/".join([self.server_url, self.application,
                                 self.api_version, self.service_uri])
        if pk is not None:
            absolute_uri += "%s/" % pk
        service_kwargs = service_kwargs or {}
        return absolute_uri % service_kwargs
