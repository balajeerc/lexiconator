"""Python wrapper for the Wordnik API. 

This API implements all the methods described at http://developer.wordnik.com/docs

maintainer: Robin Walsh (robin@wordnik.com)
"""

import helpers      ## helper functions for this module
import httplib, os

from optparse import OptionParser
from xml.etree import ElementTree
from sys import stdout, stderr

try:
    import simplejson as json
except ImportError:
    import json

DEFAULT_HOST    = "api.wordnik.com"
DEFAULT_URI     = "/v4"
DEFAULT_URL     = "http://" + DEFAULT_HOST + DEFAULT_URI

FORMAT_JSON     = "json"
FORMAT_XML      = "xml" 
DEFAULT_FORMAT  = FORMAT_JSON

class RestfulError(Exception):
    """Raised when response from REST API indicates an error has occurred."""

class InvalidRelationType(Exception):
    """Raised if Wordnik.related method is passed invalid relation type."""

class NoAPIKey(Exception):
    """Raised if we don't get an API key."""

class MissingParameters(Exception):
    """Raised if we try to call an API method with required parameters missing"""
    
class Wordnik(object):
    
    """
    A generic Wordnik object. Use me to interact with the Wordnik API.
    
    All of my methods can be called in multiple ways. All positional
    arguments passed into one of my methods (with the exception of "format")
    will be substituted for the correponding path parameter, if possible.
    For example, consider the "get_word_examples" method. The URI path is:
    
    /word.{format}/{word}/examples
    
    So we can skip format (default format is JSON) and infer that the first
    positional argument is the word we want examples for. Hence:
    
    Wordnik.word_get_examples('cat')
    
    All other (non-path) arguments are keyword arguments. The "format"
    paramater can be passed in this way as well. Hence:
    
    Wordnik.word_get_examples('cat', format='xml', limit=500)
    
    In the case where you're making a POST, you will need a "body" keyword:
    
    Wordnik.word_list_put(wordListId=1234, body="Some HTTP body")    
    """
    
    
    def __init__(self, api_key=None, username=None, password=None, beta=False):
        """
        Initialize a Wordnik object. You must pass in an API key when
        you make a new Wordnik. We don't validate the API key until the
        first call against the API is made, at which point you'll find
        out if it's good.
        
        If you also pass in a username and password, we will try to get an
        auth token so you can use the Wordnik authenticated methods.
        Alternatively, you can call Wordnik.authenticate(user, pass)
        """
        
        if api_key is None:
            raise NoAPIKey("No API key passed to our constructor")
        
        self._api_key = api_key
        self.username = username
        self.password = password
        self.token    = None
        self.beta     = beta

        self._http_code = None
        
        if username and password:
            try:
                j = self.account_get_authenticate(username, password=password)
                self.token = j['token']
            except:
                raise RestfulError("Could not authenticate with the given username and password")
        
        
    @classmethod
    def _populate_methods(klass):
        """This will create all the methods we need to interact with
        the Wordnik API"""
        
        ## there is a directory called "endpoints"
        #basedir = os.path.dirname(__file__)
        
         ## there is a directory called "endpoints"
        basedir = "wordnik/endpoints/"
        filenames = ['account.json','word.json','wordList.json','wordLists.json','words.json']
        for filename in filenames:
            j = json.load(open(basedir+filename))
            Wordnik._create_methods(j)
            
    @classmethod
    def _create_methods(klass, jsn):
        """A helper method that will populate this module's namespace
        with methods (parsed directlly from the Wordnik API's output)
        """
        endpoints = jsn['endPoints']
    
        for method in endpoints:
            path = method['path']
            for op in method['operations']:
                summary = op['summary']
                httpmethod = op['httpMethod']
                params = op['parameters']
                response = op['response']
    
                ## a path like: /user.{format}/{username}/wordOfTheDayList/{permalink} (GET)
                ## will get translated into method: user_get_word_of_the_day_list
                methodName  = helpers.normalize(path, httpmethod.lower())
                docs        = helpers.generate_docs(params, response, summary, path)
                method      = helpers.create_method(methodName, docs, params, path, httpmethod.upper())
                
                setattr( Wordnik, methodName, method )
    
    def _run_command(self, command_name, *args, **kwargs):
        if 'api_key' not in kwargs:
            kwargs.update( {"api_key": self._api_key} )
        if self.token:
            kwargs.update( {"auth_token": self.token} )
        
        command                 = getattr(self, command_name)
        (path, headers, body)   = helpers.process_args(command._path, command._params, args, kwargs)
        httpmethod              = command._http
        
        return self._do_http(path, headers, body, httpmethod, beta=self.beta)
        
    def multi(self, calls, **kwargs):
        """Multiple calls, batched. This is a "special case" method
        in that it's not automatically generated from the API documentation.
        That's because, well, it's undocumented. Here's how you use it:
        
        Wordnik.multi( [call1, call2, call3 ], **kwargs)
        
        where each "call" is (word, resource, {param1: value1, ...} )
        So we could form a batch call like so:
        
        calls = [("dog","examples"),("cat","definitions",{"limit":500})]
        
        Wordnik.multi(calls, format="xml")
        
        """
        
        path = "/word.%s?multi=true" % (kwargs.get('format') or DEFAULT_FORMAT)
        
        
        for calls_made, call in enumerate(calls):
            word = call[0]
            resource = call[1]
            if len(call) >= 3:
                otherParams = call[2]
            else:
                otherParams = {}
            ## Add the first resource to the URL
            path += "&resource.{0}={1}/{2}".format(calls_made,word,resource)
            for key,val in otherParams.items():
                ## Add potential extra params to the URL
                path += "&{0}.{1}={2}".format(key, calls_made, val)
        
        headers = { "api_key": self._api_key }
        if self.token:
            headers.update( {"auth_token": self.token} )
        
        return self._do_http(path, headers, beta=self.beta)
    
    def authenticate(self, username, password):
        """A convenience method to get an auth token in case the object was 
        not instantiated with a username and a password.
        """

        try:
            resp = self.account_get_authenticate(username, password=password, 
                                                 format='json')
        except:
            raise RestfulError("Could not authenticate with the given username and password")
        else:
            self.token = resp['token']
            return True
    
    def _do_http(self, uri, headers, body=None, method="GET", beta=False):
        """This wraps the HTTP call. This may get factored out in the future."""
        ## If there's a body, it will be JSON.
        if body:
            headers.update( {"Content-Type": "application/json"})

        ## make the HTTP connection (to the right host)
        full_uri = DEFAULT_URI + uri
        conn = httplib.HTTPConnection(DEFAULT_HOST)
        if beta:
            conn = httplib.HTTPConnection("beta.wordnik.com")

        ## Make the request, get the response
        conn.request(method, full_uri, body, headers)
        response = conn.getresponse()
        ## Save the response code for later (in case we need it)
        self._http_code = response.status

        ## Return meaningful structured data if the call was OK
        if response.status == httplib.OK:
            text = response.read()
            format_ = headers.get('format', DEFAULT_FORMAT)
            if format_ == FORMAT_JSON:
                return json.loads(text)
            elif format_ == FORMAT_XML:
                return ElementTree.XML(text)
        
        ## Otherwise just return what we got
        else:
            return response.read()
            #print >> stderr, "{0}: {1}".format(response.status, response.reason)
