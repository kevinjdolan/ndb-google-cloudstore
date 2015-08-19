import os
import preparePythonPath

if 'DATASTORE_HOST' in os.environ:
    del os.environ['DATASTORE_HOST']

os.environ['DATASTORE_SERVICE_ACCOUNT'] = '1000212703136-2agt08r76gaph77nn1tgk4btj56fo630@developer.gserviceaccount.com'
os.environ['DATASTORE_PRIVATE_KEY_FILE'] = '/Users/kevindolan/metric/metric/metric-page-dc7e7702bb18.p12'

os.environ['DATASTORE_DATASET'] = "metric-page"
os.environ['DATASTORE_APP_ID'] = "metric-page"
os.environ['APPLICATION_ID'] = "metric-page"

from google.appengine.ext import ndb

ndb.Model._use_cache = False
ndb.Model._use_memcache = False

class TestModel(ndb.Model):

    hello = ndb.StringProperty()

testModel = TestModel(hello='world')
testModel.put()