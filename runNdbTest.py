import datetime
import os
import sys

# make sure to drop any appengine runtimes already on the path
for item in list(sys.path):
    if item.endswith('google_appengine'):
        sys.path.remove(item)

# add our custom runtimes to the path
sys.path.append('./google_appengine-1.9.25') # note: this contains a symlink to protobuf because i'm dumb
sys.path.append('./googledatastore-v1beta2-rev1-2.1.2')

import googledatastore
from google.appengine.ext import ndb

# set the environment variables to use the GCD test server

os.environ['DATASTORE_HOST'] = "http://localhost:8080"
os.environ['DATASTORE_DATASET'] = "test"
os.environ['DATASTORE_APP_ID'] = "test"
os.environ['APPLICATION_ID'] = "test"

# mock the memcache stub, since ndb uses it pretty heavily
from google.appengine.ext import testbed
testbed = testbed.Testbed()
testbed.activate()
testbed.init_memcache_stub()


class TestModel(ndb.Model):

    name = ndb.StringProperty()
    birthdatetime = ndb.DateTimeProperty()
    birthday = ndb.DateProperty()

print "---"

# model = TestModel(
#     key=ndb.Key('TestModel', 4573968371548160),
#     name="Mike",
#     birthdatetime=datetime.datetime(1988,11,19,5,0,0),
#     birthday=datetime.date(1988,11,19),
# )
# key = model.put()

# print key

key = ndb.Key('TestModel', 4573968371548160)
model = key.get()
print model