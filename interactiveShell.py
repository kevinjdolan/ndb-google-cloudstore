import os
import sys
import preparePythonPath

os.environ['APPLICATION_ID'] = sys.argv[1]
os.environ['DATASTORE_APP_ID'] = sys.argv[1]
if len(sys.argv) > 2:
    os.environ['DATASTORE_SERVICE_ACCOUNT'] = sys.argv[2]
    os.environ['DATASTORE_PRIVATE_KEY_FILE'] = sys.argv[3]

from google.appengine.ext import ndb

ndb.Model._use_cache = False
ndb.Model._use_memcache = False

import code
code.interact(local=locals())