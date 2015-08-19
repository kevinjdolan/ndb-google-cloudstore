import datetime
import unittest
import random
import logging
import os
import time
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

# classes for testing

class AutoDateModel(ndb.Model):

    autoNow = ndb.DateTimeProperty(auto_now=True)
    autoNowAdd = ndb.DateTimeProperty(auto_now_add=True)

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

class PickleableObject(object):

    def __init__(self, stringValue):
        self.stringValue = stringValue

    def __eq__(self, other):
        return other.stringValue == self.stringValue

class QueryableModel(ndb.Model):

    integerProperty = ndb.IntegerProperty()
    integerProperty2 = ndb.IntegerProperty()
    integerProperty5 = ndb.IntegerProperty()
    floatProperty = ndb.FloatProperty()
    booleanProperty = ndb.BooleanProperty()
    stringProperty = ndb.StringProperty()
    dateTimeProperty = ndb.DateTimeProperty()
    dateProperty = ndb.DateProperty()
    timeProperty = ndb.TimeProperty()
    keyProperty = ndb.KeyProperty()
    structuredProperty = ndb.StructuredProperty(EmbeddedModel)
    structuredPropertyRepeated = ndb.StructuredProperty(EmbeddedRepeatedModel)
    integerRepeatedProperty = ndb.IntegerProperty(repeated=True)

class SimpleModel(ndb.Model):

    name = ndb.StringProperty()

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

    def testAutoDate(self):
        time1 = datetime.datetime.utcnow()
        time.sleep(0.01)
        model1 = AutoDateModel()
        key = model1.put()
        time.sleep(0.01)
        model2 = key.get()
        time.sleep(0.01)
        time2 = datetime.datetime.utcnow()
        self.assertEqual(model1.autoNow, model2.autoNow)
        self.assertEqual(model1.autoNowAdd, model2.autoNowAdd)
        self.assertTrue(time1 < model1.autoNow < time2)
        self.assertTrue(time1 < model1.autoNowAdd < time2)
        time.sleep(0.01)
        model2.put()
        time.sleep(0.01)
        time3 = datetime.datetime.utcnow()
        model3 = key.get()
        self.assertEqual(model2.autoNow, model3.autoNow)
        self.assertEqual(model2.autoNowAdd, model3.autoNowAdd)
        self.assertNotEqual(model1.autoNow, model3.autoNow)
        self.assertEqual(model1.autoNowAdd, model3.autoNowAdd)
        self.assertTrue(time2 < model3.autoNow < time3)
        self.assertTrue(time1 < model3.autoNowAdd < time2)

    def testAutoId(self):
        model1 = SimpleModel(name="kevin")
        model2 = SimpleModel(name="mike")
        key1 = model1.put()
        key2 = model2.put()
        self.assertIsNotNone(key1)
        self.assertIsNotNone(key2)
        self.assertEqual(key1, model1.key)
        self.assertEqual(key2, model2.key)
        self.assertNotEqual(key1, key2)
        model1Fresh = key1.get()
        model2Fresh = key2.get()
        self.assertEqual("kevin", model1Fresh.name)
        self.assertEqual("mike", model2Fresh.name)
        self.assertEqual(key1, model1Fresh.key)
        self.assertEqual(key2, model2Fresh.key)

    def testClobberingId(self):
        model1 = SimpleModel(name="kevin")
        key1 = model1.put()
        model2 = SimpleModel(id=key1.id(), name="sam")
        key2 = model2.put()
        self.assertEqual(key1, key2)
        model3 = key1.get()
        self.assertEqual("sam", model3.name)
        model4 = SimpleModel(key=key1, name="smith")
        model4.put()
        model5 = key1.get()
        self.assertEqual("smith", model5.name)

    def testDelete(self):
        model1 = SimpleModel(name="ratner")
        key = model1.put()
        key.delete()
        model2 = key.get()
        self.assertIsNone(model2)

    def testDeleteMulti(self):
        model1 = SimpleModel(name="ratner")
        model2 = SimpleModel(name="crisple")
        key1 = model1.put()
        key2 = model2.put()
        ndb.delete_multi([key1, key2])
        model3 = key1.get()
        model4 = key2.get()
        self.assertIsNone(model3)
        self.assertIsNone(model4)

    def testPutMultiGetMulti(self):
        model1 = SimpleModel(name="kevin")
        model2 = SimpleModel(name="mike")
        keys = ndb.put_multi([model1, model2])
        self.assertEqual(model1.key, keys[0])
        self.assertEqual(model2.key, keys[1])
        models = ndb.get_multi(keys)
        self.assertEqual(models[0].name, "kevin")
        self.assertEqual(models[0].key, keys[0])
        self.assertEqual(models[1].name, "mike")
        self.assertEqual(models[1].key, keys[1])

    def testPutMultiGetMultiWithParent(self):
        model1 = SimpleModel(name="kevin", parent=ndb.Key('Parent', randomString(10)))
        model2 = SimpleModel(name="mike", parent=ndb.Key('Parent', randomString(10)))
        keys = ndb.put_multi([model1, model2])
        self.assertEqual(model1.key, keys[0])
        self.assertEqual(model2.key, keys[1])
        models = ndb.get_multi(keys)
        self.assertEqual(models[0].name, "kevin")
        self.assertEqual(models[0].key, keys[0])
        self.assertEqual(models[1].name, "mike")
        self.assertEqual(models[1].key, keys[1])

    def testMissingResult(self):
        key = ndb.Key(SimpleModel, randomString(32))
        model = key.get()
        self.assertIsNone(model)

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

    def testStringId(self):
        id = randomString(10)
        model = SimpleModel(id=id, name="tony")
        key = model.put()
        self.assertEqual(key.id(), id)
        copy = key.get()
        self.assertEqual(copy.name, "tony")
        self.assertEqual(copy.key.id(), id)

class TestNdbWithScaffold(unittest.TestCase):

    def setUp(self):
        # will clobber the set of queryable models
        models = []
        for i in range(0, 10):
            models.append(QueryableModel(
                key=ndb.Key('Parent', 1 + (i / 2), QueryableModel, 1 + i),
                integerProperty=i,
                integerProperty2=i/2,
                integerProperty5=i/5,
                floatProperty=i+0.5,
                booleanProperty=(i>=5),
                stringProperty=string.ascii_lowercase[i],
                dateTimeProperty=datetime.datetime(2015,8,i+1),
                dateProperty=datetime.date(2015,8,i+1),
                timeProperty=datetime.time(i, 0),
                keyProperty=ndb.Key('Arbitrary', i+1),
                structuredProperty=EmbeddedModel(
                    stringProperty=string.ascii_lowercase[i]
                ),
                structuredPropertyRepeated=EmbeddedRepeatedModel(
                    stringRepeatedProperty=[
                        string.ascii_lowercase[i],
                        string.ascii_lowercase[i+5],
                        string.ascii_lowercase[i+10],
                    ]
                ),
                integerRepeatedProperty=[i, i+5, i+10],
            ))
        ndb.put_multi(models)

    def testGet(self):
        model = ndb.Key('Parent', 1, QueryableModel, 1).get()
        self.assertEqual(model.integerProperty, 0)

    def testQueryAllCount(self):
        count = QueryableModel.query().count()
        self.assertEqual(10, count)

    def testQueryAllFetch(self):
        models = QueryableModel.query().fetch()
        self.assertEqual(10, len(models))
        uniqueInts = set([model.integerProperty for model in models])
        self.assertEqual(uniqueInts, set(range(0,10)))

    def testQueryAllFetchLimit(self):
        models = QueryableModel.query().fetch(2)
        self.assertEqual(2, len(models))

    def testQueryAllFetchOrder(self):
        models = QueryableModel.query()\
            .order(QueryableModel.integerProperty)\
            .fetch(2)
        self.assertEqual(2, len(models))
        self.assertEqual(0, models[0].integerProperty)
        self.assertEqual(1, models[1].integerProperty)

    def testQueryAllFetchOrderMulti(self):
        models = QueryableModel.query()\
            .order(
                QueryableModel.integerProperty5,    
                QueryableModel.integerProperty,
            )\
            .fetch(2)
        self.assertEqual(2, len(models))
        self.assertEqual(0, models[0].integerProperty)
        self.assertEqual(1, models[1].integerProperty)

    def testQueryAllFetchOrderMultiReverseBoth(self):
        models = QueryableModel.query()\
            .order(
                -QueryableModel.integerProperty5,    
                -QueryableModel.integerProperty,
            )\
            .fetch(2)
        self.assertEqual(2, len(models))
        self.assertEqual(9, models[0].integerProperty)
        self.assertEqual(8, models[1].integerProperty)

    def testQueryAllFetchOrderMultiReverseFirst(self):
        models = QueryableModel.query()\
            .order(
                -QueryableModel.integerProperty5,    
                QueryableModel.integerProperty,
            )\
            .fetch(2)
        self.assertEqual(2, len(models))
        self.assertEqual(5, models[0].integerProperty)
        self.assertEqual(6, models[1].integerProperty)

    def testQueryAllFetchOrderMultiReverseSecond(self):
        models = QueryableModel.query()\
            .order(
                QueryableModel.integerProperty5,    
                -QueryableModel.integerProperty,
            )\
            .fetch(2)
        self.assertEqual(2, len(models))
        self.assertEqual(4, models[0].integerProperty)
        self.assertEqual(3, models[1].integerProperty)

    def testQueryAllFetchOrderReverse(self):
        models = QueryableModel.query()\
            .order(-QueryableModel.integerProperty)\
            .fetch(2)
        self.assertEqual(2, len(models))
        self.assertEqual(9, models[0].integerProperty)
        self.assertEqual(8, models[1].integerProperty)


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