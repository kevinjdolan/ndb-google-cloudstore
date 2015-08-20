# ndb-google-cloudstore

This is a fork of the google app engine runtime to support utilizing ndb outside of 
the context of Google AppEngine, through the google cloud datastore.

## Background:

While investigating the required effort to craft a database service stub using
the Google Cloud Datastore RPC apis, it became clear to me that there were numerous
statements peppered throughout the code to support using Google Cloud Datastore
directly.

In fact, the implementation of make_default_context appears to prefer using GCD
when certain environment variables are set.

```
def make_default_context():
  # XXX Docstring
  datastore_app_id = os.environ.get(_DATASTORE_APP_ID_ENV, None)
  datastore_project_id = os.environ.get(_DATASTORE_PROJECT_ID_ENV, None)
  if datastore_app_id or datastore_project_id:
    # We will create a Cloud Datastore context.
    ....
  return make_context()
```

Unfortunately, simply setting these values did not appear to do the trick. There
are numerous pieces of code operating on the datastore API with ever-so-slightly
different names. For the most part, this is simply changing plural names to
singular names (which I assume is to conform to some internal style guide.) Some
other changes are bigger, but for the most part, it's easy to guess what happened.

My running theory is that at some point, there was an effort to integrate GCD
RPCs into app engine, either to support the use case of using outside of AppEngine,
or to unify apis and clean up code.

However, this effort was probably done with an old version of the GCD RPCs, and 
possibly aborted for whatever reason, or simply in-progress.

There is also a test suite to make sure that it works for the most part.

This was a rabbit hole and I am not proud of myself.

This pull request summarizes all changes:

https://github.com/kevinjdolan/ndb-google-cloudstore/pull/1

## Requirements

The googledatastore package requires httplib2 and oauthclient.

## Included sources:

Embedded in this repo are various python libraries written by google. They are:

googledatastore-v1beta2-rev1-2.1.0
Google Cloud Datstore client RPC libraries in python.
Downloaded from: https://pypi.python.org/pypi/googledatastore

gcd-v1beta2-rev1-2.1.1
Google Cloud Datastore development server.
Downloaded from: https://cloud.google.com/datastore/docs/downloads

protobuf-2.5.0
Google's Protobuffer python library
Downloaded from: https://pypi.python.org/pypi/protobuf/2.5.0

google_appengine-1.9.25
Google App engine Runtime
Downloaded from: https://cloud.google.com/appengine/downloads?hl=en

The branch `original` contains unmodified versions of these files. 
The branch `master` contains a modified version of google_appengine-1.9.25.

## Running the tests:

First create the test datastore (you only need to do this once)

> ./createDevServer.sh

Then start the test datastore:

> ./startDevServer.sh

Finally, set up the proper environment and run the test cases:

> python runNdbTests.py

## Running the interactive shell:

The following will get you an interactive shell on a fresh GCE instance
running Wheezy:

> sudo apt-get install git-core
> sudo apt-get install python-setuptools
> sudo easy_install httplib2
> sudo easy_install oauth2client
> git clone https://github.com/kevinjdolan/ndb-google-cloudstore
> cd ndb-google-cloudstore
> python interactiveShell.py "s~your-project-id" "your-service-account@developer.gserviceaccount.com" "/path/to/key.pem"
>>> class Test(ndb.Model):
...     name = ndb.StringProperty()
... 
>>> testModel = Test(name="hello world")
>>> testKey = testModel.put()
>>> testKey
Key('Test', 6483219914424320)
>>> testModelCopy = testKey.get()
>>> testModelCopy
Test(key=Key('Test', 6483219914424320), name=u'hello world')

## Caveats

`ndb.Model.allocate_ids()` won't work with the API provided by google cloudstorage,
because it does not return a range of keys. Instead, it returns a set of allocated
keys. For this to be functional, I've changed the signature of ndb.Model.allocate_ids() 
(and the async version) to instead return a list of keys of the provided size. 
The max argument is not supported.

Exceptions produced by the RPC are generally forwarded directly through to the 
application, rather than being wrapped or handled elegantly. This means that
the types of exceptions thrown by errors in the datastore will be different, which
could obviously break code. The only exceptional case I have handled specifically
is the issue of contention on transaction commits, which I probably don't do correctly --
but it does make bad transational test I wrote work.

Geo Point properties are not supported.

Transaction support is not likely done correctly...

I have observed no end of problems when using the google cloud authorization provided
by google compute engine. You must disable that for this to work for some reason
far, far beyond my skillset.