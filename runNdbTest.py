import datetime
import unittest
import random
import logging
import os
import sys
import string

# make sure to drop any appengine runtimes already on the path
for item in list(sys.path):
    if item.endswith('google_appengine'):
        sys.path.remove(item)

# add our custom runtimes to the path
sys.path.append('./google_appengine-1.9.25') # note: this contains a symlink to protobuf because i'm dumb
sys.path.append('./googledatastore-v1beta2-rev1-2.1.2')

import googledatastore
from google.appengine.api import users
from google.appengine.ext import ndb

class PickleableObject(object):

    def __init__(self, stringValue):
        self.stringValue = stringValue

    def __eq__(self, other):
        return other.stringValue == self.stringValue

class EmbeddedModel(ndb.Model):

    stringProperty = ndb.StringProperty()

class EmbeddedRepeatedModel(ndb.Model):

    stringRepeatedProperty = ndb.StringProperty(repeated=True)

class EveryTypeModel(ndb.Model):

    # TODO: test BlobKeyProperty, ComputedProperty, UserProperty, GeoPtProperty

    integerProperty = ndb.IntegerProperty()
    floatProperty = ndb.FloatProperty()
    booleanProperty = ndb.BooleanProperty()
    stringProperty = ndb.StringProperty()
    textProperty = ndb.TextProperty()
    blobProperty = ndb.BlobProperty()
    dateTimeProperty = ndb.DateTimeProperty()
    dateProperty = ndb.DateProperty()
    timeProperty = ndb.TimeProperty()
    keyProperty = ndb.KeyProperty()
    structuredProperty = ndb.StructuredProperty(EmbeddedModel)
    structuredProperty2 = ndb.StructuredProperty(EmbeddedRepeatedModel)
    localStructuredProperty = ndb.LocalStructuredProperty(EmbeddedModel)
    localStructuredProperty2 = ndb.LocalStructuredProperty(EmbeddedRepeatedModel)
    jsonProperty = ndb.JsonProperty()
    pickleProperty = ndb.PickleProperty()
    genericProperty = ndb.GenericProperty()

    integerRepeatedProperty = ndb.IntegerProperty(repeated=True)
    floatRepeatedProperty = ndb.FloatProperty(repeated=True)
    booleanRepeatedProperty = ndb.BooleanProperty(repeated=True)
    stringRepeatedProperty = ndb.StringProperty(repeated=True)
    textRepeatedProperty = ndb.TextProperty(repeated=True)
    blobRepeatedProperty = ndb.BlobProperty(repeated=True)
    dateTimeRepeatedProperty = ndb.DateTimeProperty(repeated=True)
    dateRepeatedProperty = ndb.DateProperty(repeated=True)
    timeRepeatedProperty = ndb.TimeProperty(repeated=True)
    keyRepeatedProperty = ndb.KeyProperty(repeated=True)
    structuredRepeatedProperty = ndb.StructuredProperty(EmbeddedModel, repeated=True)
    localStructuredRepeatedProperty = ndb.LocalStructuredProperty(EmbeddedModel, repeated=True)
    jsonRepeatedProperty = ndb.JsonProperty(repeated=True)
    pickleRepeatedProperty = ndb.PickleProperty(repeated=True)
    genericRepeatedProperty = ndb.GenericProperty(repeated=True)

# methods for generating random input

def randomAnything():
    return random.choice([randomString(32), randomBool(), random.random(), random.randint(0,1000)])

def randomBool():
    return random.random() < 0.5

def randomDate():
    return datetime.date(random.randint(1990,2000), random.randint(1,12), random.randint(1,28))

def randomDateTime():
    return datetime.datetime(random.randint(1990,2000), random.randint(1,12), random.randint(1,28), random.randint(0,23), random.randint(0,59), random.randint(0,59))

def randomGeo():
    return ndb.GeoPt(random.uniform(-90, 90), random.uniform(-180, 180))

def randomKey():
    return ndb.Key('Test', randomString(32))

def randomString(length, charset=string.printable):
    characters = []
    for i in xrange(0, length):
        characters.append(random.choice(charset))
    return "".join(characters)

def randomTime():
    return datetime.time(random.randint(0,23), random.randint(0,59), random.randint(0,59))

class TestNdb(unittest.TestCase):

    def testPutAndGetMultiType(self):
        model = EveryTypeModel(
            integerProperty = random.randint(0,1000),
            floatProperty = random.random(),
            booleanProperty = randomBool(),
            stringProperty = randomString(100),
            textProperty = randomString(2000),
            blobProperty = randomString(2000),
            dateTimeProperty = randomDateTime(),
            dateProperty = randomDate(),
            timeProperty = randomTime(),
            keyProperty = randomKey(),
            structuredProperty = EmbeddedModel(stringProperty=randomString(32)),
            structuredProperty2 = EmbeddedRepeatedModel(stringRepeatedProperty=[randomString(32), randomString(32)]),
            localStructuredProperty = EmbeddedModel(stringProperty=randomString(32)),
            localStructuredProperty2 = EmbeddedRepeatedModel(stringRepeatedProperty=[randomString(32), randomString(32)]),
            jsonProperty = {'key': randomString(32)},
            pickleProperty = PickleableObject(randomString(32)),
            genericProperty = randomAnything(),

            integerRepeatedProperty = [random.randint(0,1000), random.randint(0,1000)],
            floatRepeatedProperty = [random.random(), random.random()],
            booleanRepeatedProperty = [randomBool(), randomBool()],
            stringRepeatedProperty = [randomString(100), randomString(100)],
            textRepeatedProperty = [randomString(2000), randomString(2000)],
            blobRepeatedProperty = [randomString(2000), randomString(2000)],
            dateTimeRepeatedProperty = [randomDateTime(), randomDateTime()],
            dateRepeatedProperty = [randomDate(), randomDate()],
            timeRepeatedProperty = [randomTime(), randomTime()],
            keyRepeatedProperty = [randomKey(), randomKey()],
            structuredRepeatedProperty = [
                EmbeddedModel(stringProperty=randomString(32)),
                EmbeddedModel(stringProperty=randomString(32)),
            ],
            localStructuredRepeatedProperty = [
                EmbeddedModel(stringProperty=randomString(32)),
                EmbeddedModel(stringProperty=randomString(32)),
            ],
            jsonRepeatedProperty = [{'key': randomString(32)}, {'key': randomString(32)}],
            pickleRepeatedProperty = [
                PickleableObject(randomString(32)),
                PickleableObject(randomString(32)),
            ],
            genericRepeatedProperty =  [randomAnything(), randomAnything()],
        )
        key = model.put()
        self.assertIsNotNone(key.id())

        fresh = key.get()
        self.assertIsNot(model, fresh)
        self.assertEqual(model.to_dict(), fresh.to_dict())
        self.assertEqual(model.key, fresh.key)

if __name__ == '__main__':
    # set the environment variables to use the GCD test server
    os.environ['DATASTORE_HOST'] = "http://localhost:8080"
    os.environ['DATASTORE_DATASET'] = "test"
    os.environ['DATASTORE_APP_ID'] = "test"
    os.environ['APPLICATION_ID'] = "test"

    # disable the cache for more accurate test conclusions
    ndb.Model._use_cache = False
    ndb.Model._use_memcache = False

    unittest.main()