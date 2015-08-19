import datetime
import unittest
import random
import logging
import os
import time
import sys
import string
import multiprocessing

import preparePythonPath

import googledatastore
from google.appengine.ext import ndb

# classes for testing

class AutoDateModel(ndb.Model):

    autoNow = ndb.DateTimeProperty(auto_now=True)
    autoNowAdd = ndb.DateTimeProperty(auto_now_add=True)

class Counter(ndb.Model):

    count = ndb.IntegerProperty()

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
    structuredRepeatedProperty = ndb.StructuredProperty(EmbeddedModel, repeated=True)
    structuredPropertyRepeated = ndb.StructuredProperty(EmbeddedRepeatedModel)
    integerRepeatedProperty = ndb.IntegerProperty(repeated=True)

class SimpleModel(ndb.Model):

    name = ndb.StringProperty()

class SimpleQueryableModel(ndb.Model):

    integerProperty = ndb.IntegerProperty()

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

    def testAllocateIds(self):
        keys = SimpleModel.allocate_ids(5)
        self.assertEqual(5, len(keys))
        for key in keys:
            self.assertEqual(key.kind(), 'SimpleModel')
            self.assertIsNotNone(key.id())

    def testAllocateIdsWithParent(self):
        keys = SimpleModel.allocate_ids(5, parent=ndb.Key('Parent', 1))
        self.assertEqual(5, len(keys))
        for key in keys:
            self.assertEqual(key.kind(), 'SimpleModel')
            self.assertEqual(key.parent(), ndb.Key('Parent', 1))
            self.assertIsNotNone(key.id())

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

    def testAsyncPutAndGet(self):
        model1 = SimpleModel(name="kevin")
        key1Future = model1.put_async()
        self.assertFalse(key1Future.done()) # is this always true?
        key1 = key1Future.get_result()
        self.assertTrue(key1Future.done())
        model2Future = key1.get_async()
        self.assertFalse(model2Future.done()) # is this always true?
        model2 = model2Future.get_result()
        self.assertTrue(model2Future.done())
        self.assertEqual(model2.name, "kevin")

    def testAsyncTasklet(self):
        @ndb.tasklet
        def run():
            model1 = SimpleModel(name="kevin")
            model2 = SimpleModel(name="mike")
            [key1, key2] = (yield ndb.put_multi_async([model1, model2]))
            [model3, model4] = (yield (key1.get_async(), key2.get_async()))
            raise ndb.Return([model3.name, model4.name])
        future = run()
        result = future.get_result()
        self.assertEqual(["kevin", "mike"], result)

    def testAsyncWaitMulti(self):
        model1 = SimpleModel(name="kevin")
        model2 = SimpleModel(name="mike")
        [key1, key2] = ndb.put_multi([model1, model2])
        future1 = key1.get_async()
        future2 = key2.get_async()
        self.assertFalse(future1.done()) # is this always true?
        self.assertFalse(future2.done())
        ndb.Future.wait_all([future1, future2])
        self.assertTrue(future1.done())
        self.assertTrue(future2.done())
        self.assertEqual("kevin", future1.get_result().name)
        self.assertEqual("mike", future2.get_result().name)

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

    def testTransaction(self):
        model = Counter(count=0)
        key = model.put()

        @ndb.transactional(retries=0)
        def increment():
            fresh = key.get()
            fresh.count += 1
            fresh.put()
            return fresh.count

        count1 = increment()
        count2 = increment()
        self.assertEqual(count1, 1)
        self.assertEqual(count2, 2)

        fresh = key.get()
        self.assertEqual(fresh.count, 2)

    def testTransactionWithException(self):
        model = Counter(count=0)
        key = model.put()

        @ndb.transactional(retries=0)
        def increment():
            fresh = key.get()
            fresh.count += 1
            fresh.put()
            raise ValueError

        with self.assertRaises(ValueError):
            increment()

        fresh = key.get()
        self.assertEqual(fresh.count, 0)

    # TODO: test me on foreign db
    # def testTransactionSimultaneous(self):
    #     model = Counter(count=0)
    #     key = model.put()

    #     TestNdb.slowTries = 0
    #     TestNdb.fastTries = 0

    #     @ndb.transactional
    #     def incrementSlow():
    #         TestNdb.slowTries += 1
    #         print "slow: start"
    #         time.sleep(0.1)
    #         print "slow: get"
    #         fresh = key.get()
    #         print "slow: got"
    #         fresh.count += 1
    #         time.sleep(0.3)
    #         print "slow: put"
    #         fresh.put()
    #         print "slow: putted"
    #         time.sleep(0.1)
    #         print "slow: done"

    #     @ndb.transactional
    #     def incrementFast():
    #         TestNdb.fastTries += 1
    #         print "fast: start"
    #         time.sleep(0.2)
    #         print "fast: get"
    #         fresh = key.get()
    #         print "fast: got"
    #         time.sleep(0.1)
    #         fresh.count += 1
    #         print "fast: put"
    #         fresh.put()
    #         print "fast: putted"
    #         time.sleep(0.1)
    #         print "fast: done"

    #     thread1 = multiprocessing.Thread(target=incrementSlow)
    #     thread2 = multiprocessing.Thread(target=incrementFast)

    #     thread1.start()
    #     thread2.start()

    #     thread1.join()
    #     thread2.join()

    #     fresh = key.get()
    #     self.assertEqual(fresh.count, 2)
    #     self.assertEqual(TestNdb.slowTries, 2)
    #     self.assertEqual(TestNdb.fastTries, 1)

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
                structuredRepeatedProperty=[
                    EmbeddedModel(
                        stringProperty=string.ascii_lowercase[i]
                    ),
                    EmbeddedModel(
                        stringProperty=string.ascii_lowercase[i+5]
                    ),
                    EmbeddedModel(
                        stringProperty=string.ascii_lowercase[i+10]
                    ),
                ],
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

    def testQueryAllIterLargeSet(self):
        self._setUpLargeScaffold()
        query = SimpleQueryableModel.query(ancestor=ndb.Key('Parent', 1))
        models = list(query)
        self.assertEqual(100, len(models))

    def testQueryAllGet(self):
        model = QueryableModel.query().get()
        self.assertIsNotNone(model)

    def testQueryAncestor(self):
        models = QueryableModel\
            .query(ancestor=ndb.Key('Parent', 1))\
            .fetch()
        self.assertEqual(2, len(models))
        self.assertEqual(1, models[0].key.parent().id())
        self.assertEqual(1, models[1].key.parent().id())

    def testQueryAncestorAndEquality(self):
        models = QueryableModel\
            .query(ancestor=ndb.Key('Parent', 1))\
            .filter(QueryableModel.integerProperty == 0)\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(0, models[0].integerProperty)

    def testQueryAncestorAndEqualityMissing(self):
        models = QueryableModel\
            .query(ancestor=ndb.Key('Parent', 2))\
            .filter(QueryableModel.integerProperty == 0)\
            .fetch()
        self.assertEqual(0, len(models))

    def testQueryEqualityBoolean(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.booleanProperty == True)\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertTrue(model.booleanProperty)

    def testQueryEqualityDate(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.dateProperty == datetime.date(2015,8,5))\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(datetime.date(2015,8,5), models[0].dateProperty)

    def testQueryEqualityDateTime(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.dateTimeProperty == datetime.datetime(2015,8,5))\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(datetime.datetime(2015,8,5), models[0].dateTimeProperty)

    def testQueryEqualityFloat(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.floatProperty == 4.5)\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(4.5, models[0].floatProperty)

    def testQueryEqualityInteger(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty == 4)\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(4, models[0].integerProperty)

    def testQueryEqualityIntegerMultiResult(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty2 == 2)\
            .fetch()
        self.assertEqual(2, len(models))
        self.assertEqual(2, models[0].integerProperty2)
        self.assertEqual(2, models[1].integerProperty2)

    def testQueryEqualityIntegerRepeatedProperty(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerRepeatedProperty == 5)\
            .fetch()
        self.assertEqual(2, len(models))
        self.assertIn(5, models[0].integerRepeatedProperty)
        self.assertIn(5, models[1].integerRepeatedProperty)

    def testQueryEqualityKey(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.keyProperty == ndb.Key('Arbitrary', 5))\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(ndb.Key('Arbitrary', 5), models[0].keyProperty)

    def testQueryEqualityTime(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.timeProperty == datetime.time(4,0))\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(datetime.time(4,0), models[0].timeProperty)

    def testQueryEqualityString(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.stringProperty == 'e')\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual('e', models[0].stringProperty)

    def testQueryEqualityStructuredProperty(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.structuredProperty.stringProperty == 'e')\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual('e', models[0].structuredProperty.stringProperty)

    def testQueryEqualityStructuredPropertyRepeated(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.structuredPropertyRepeated.stringRepeatedProperty == 'f')\
            .fetch()
        self.assertEqual(2, len(models))
        self.assertIn('f', models[0].structuredPropertyRepeated.stringRepeatedProperty)
        self.assertIn('f', models[1].structuredPropertyRepeated.stringRepeatedProperty)

    def testQueryEqualityStructuredRepeatedProperty(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.structuredRepeatedProperty.stringProperty == 'f')\
            .fetch()
        self.assertEqual(2, len(models))
        self.assertIn('f', [x.stringProperty for x in models[0].structuredRepeatedProperty])
        self.assertIn('f', [x.stringProperty for x in models[1].structuredRepeatedProperty])

    def testQueryGreaterBoolean(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.booleanProperty > False)\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertTrue(model.booleanProperty)

    def testQueryGreaterDate(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.dateProperty> datetime.date(2015,8,5))\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(datetime.date(2015,8,5), model.dateProperty)

    def testQueryGreaterDateTime(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.dateTimeProperty > datetime.datetime(2015,8,5))\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(datetime.datetime(2015,8,5), model.dateTimeProperty)

    def testQueryGreaterFloat(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.floatProperty > 4.5)\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(4.5, model.floatProperty)

    def testQueryGreaterInteger(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty > 4)\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(4, model.integerProperty)

    def testQueryGreaterEqualInteger(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty >= 4)\
            .fetch()
        self.assertEqual(6, len(models))
        for model in models:
            self.assertLessEqual(4, model.integerProperty)

    def testQueryGreaterIntegerRepeatedProperty(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerRepeatedProperty > 14)\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(14, max(model.integerRepeatedProperty))

    def testQueryGreaterKey(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.keyProperty > ndb.Key('Arbitrary', 5))\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(ndb.Key('Arbitrary', 5), model.keyProperty)

    def testQueryGreaterTime(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.timeProperty > datetime.time(4,0))\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(datetime.time(4,0), model.timeProperty)

    def testQueryGreaterString(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.stringProperty > 'e')\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess('e', model.stringProperty)

    def testQueryGreaterStructuredProperty(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.structuredProperty.stringProperty > 'e')\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess('e', model.structuredProperty.stringProperty)

    def testQueryGreaterStructuredPropertyRepeated(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.structuredPropertyRepeated.stringRepeatedProperty > 'o')\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(
                'o', 
               max(model.structuredPropertyRepeated.stringRepeatedProperty),
            )

    def testQueryGreaterStructuredRepeatedProperty(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.structuredRepeatedProperty.stringProperty > 'o')\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertLess(
                'o', 
                max([
                    x.stringProperty
                    for x 
                    in model.structuredRepeatedProperty
                ]),
            )

    def testQueryIn(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty.IN([0,1,2,3,4]))\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertIn(model.integerProperty, [0,1,2,3,4])

    def testQueryInequality(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty5 != 0)\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertNotEqual(0, model.integerProperty5)

    def testQueryLessInteger(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty < 5)\
            .fetch()
        self.assertEqual(5, len(models))
        for model in models:
            self.assertGreater(5, model.integerProperty)

    def testQueryLessEqualInteger(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty <= 5)\
            .fetch()
        self.assertEqual(6, len(models))
        for model in models:
            self.assertGreaterEqual(5, model.integerProperty)

    def testQueryMultipleEquality(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty == 0)\
            .filter(QueryableModel.integerProperty5 == 0)\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(0, models[0].integerProperty)

    def testQueryMultipleEqualityMissing(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty == 0)\
            .filter(QueryableModel.integerProperty5 == 1)\
            .fetch()
        self.assertEqual(0, len(models))

    def testQueryMultipleEqualityGreater(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty == 8)\
            .filter(QueryableModel.integerProperty5 > 0)\
            .fetch()
        self.assertEqual(1, len(models))
        self.assertEqual(8, models[0].integerProperty)

    def testQueryMultipleEqualityGreaterMissing(self):
        models = QueryableModel.query()\
            .filter(QueryableModel.integerProperty == 0)\
            .filter(QueryableModel.integerProperty5 > 0)\
            .fetch()
        self.assertEqual(0, len(models))

    def testQueryMultipleGreaterGreater(self):
        # Is this the correct exception?
        # This outputs a warning which is ugly... can it be suppressed?
        from googledatastore.connection import RPCError
        with self.assertRaises(RPCError):
            models = QueryableModel.query()\
                .filter(QueryableModel.integerProperty > 8)\
                .filter(QueryableModel.integerProperty5 > 0)\
                .fetch()
            self.assertEqual(1, len(models))
            self.assertEqual(9, models[0].integerProperty)

    def testQueryPaginate(self):
        query = QueryableModel.query().order(QueryableModel.integerProperty)

        results1, nextCursor1, more1 = query.fetch_page(4)
        self.assertEqual([0,1,2,3], [result.integerProperty for result in results1])
        self.assertIsNotNone(nextCursor1)
        self.assertTrue(more1)

        results2, nextCursor2, more2 = query.fetch_page(4, start_cursor=nextCursor1)
        self.assertEqual([4,5,6,7], [result.integerProperty for result in results2])
        self.assertIsNotNone(nextCursor2)
        self.assertTrue(more2)

        results3, nextCursor3, more3 = query.fetch_page(4, start_cursor=nextCursor2)
        self.assertEqual([8,9], [result.integerProperty for result in results3])
        # not sure about ideal values for these two:
        self.assertIsNotNone(nextCursor3)
        self.assertFalse(more3)

        # would we always have a cursor here?
        results4, nextCursor4, more4 = query.fetch_page(4, start_cursor=nextCursor3)
        self.assertEqual([], results4)
        # not sure about ideal values for these two:
        self.assertIsNone(nextCursor4)
        self.assertFalse(more4)

    def testQueryKeysOnly(self):
        keys = QueryableModel.query()\
            .filter(QueryableModel.integerProperty == 4)\
            .fetch(keys_only=True)
        self.assertEqual(1, len(keys))
        self.assertEqual(ndb.Key('Parent', 3, QueryableModel, 5), keys[0])

    def testQueryProjection(self):
        models = QueryableModel.query()\
            .fetch(projection=[
                QueryableModel.integerProperty, 
                QueryableModel.integerProperty5,
            ])
        self.assertEqual(10, len(models))
        for model in models:
            self.assertIsNotNone(model.integerProperty)
            self.assertIsNotNone(model.integerProperty5)
            with self.assertRaises(ndb.UnprojectedPropertyError):
                model.stringProperty

    def testQueryProjectionDistinct(self):
        models = QueryableModel.query(
                projection=[QueryableModel.integerProperty5], 
                distinct=True
            )\
            .fetch()
        self.assertEqual(2, len(models))
        self.assertEqual(set([0,1]), set([model.integerProperty5 for model in models]))

    def testQueryProjectionGroupBy(self):
        models = QueryableModel.query(
                projection=[QueryableModel.integerProperty5], 
                group_by=[QueryableModel.integerProperty5],
            )\
            .fetch()
        self.assertEqual(2, len(models))
        self.assertEqual(set([0,1]), set([model.integerProperty5 for model in models]))

    def testQueryProjectionGroupByWithExtra(self):
        from google.appengine.api.datastore_errors import BadRequestError
        with self.assertRaises(BadRequestError):
            models = QueryableModel.query(
                    projection=[
                        QueryableModel.integerProperty,
                        QueryableModel.integerProperty5,
                    ], 
                    group_by=[QueryableModel.integerProperty5],
                )\
                .fetch()

    def _setUpLargeScaffold(self):
        scaffoldModels = []
        for i in range(0, 100):
            scaffoldModels.append(SimpleQueryableModel(
                parent=ndb.Key('Parent', 1),
                id=i+1,
                integerProperty=i,
            ))
        ndb.put_multi(scaffoldModels)

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