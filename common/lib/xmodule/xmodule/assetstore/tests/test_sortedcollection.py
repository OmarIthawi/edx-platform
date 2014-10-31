"""
Tests the SortedCollection class.
http://code.activestate.com/recipes/577197-sortedcollection/
"""

import unittest
from random import choice
from operator import itemgetter
from copy import copy
from xmodule.assetstore import SortedCollection


class SortedCollectionTest(unittest.TestCase):
    """
    Tests for the SortedCollection class.
    """

    def ve2no(self, f, *args):
        'Convert ValueError result to -1'
        try:
            return f(*args)
        except ValueError:
            return -1

    def slow_index(self, seq, k):
        'Location of match or -1 if not found'
        for i, item in enumerate(seq):
            if item == k:
                return i
        return -1

    def slow_find(self, seq, k):
        'First item with a key equal to k. -1 if not found'
        for item in seq:
            if item == k:
                return item
        return -1

    def slow_find_le(self, seq, k):
        'Last item with a key less-than or equal to k.'
        for item in reversed(seq):
            if item <= k:
                return item
        return -1

    def slow_find_lt(self, seq, k):
        'Last item with a key less-than k.'
        for item in reversed(seq):
            if item < k:
                return item
        return -1

    def slow_find_ge(self, seq, k):
        'First item with a key-value greater-than or equal to k.'
        for item in seq:
            if item >= k:
                return item
        return -1

    def slow_find_gt(self, seq, k):
        'First item with a key-value greater-than or equal to k.'
        for item in seq:
            if item > k:
                return item
        return -1

    def test_numerical(self):
        pool = [1.5, 2, 2.0, 3, 3.0, 3.5, 4, 4.0, 4.5]
        for i in range(500):
            for num_nums in range(6):
                num_list = [choice(pool) for i in range(num_nums)]
                coll = SortedCollection(num_list)
                num_list.sort()
                for probe in pool:
                    self.assertEquals(repr(self.ve2no(coll.index, probe)), repr(self.slow_index(num_list, probe)))
                    self.assertEquals(repr(self.ve2no(coll.find, probe)), repr(self.slow_find(num_list, probe)))
                    self.assertEquals(repr(self.ve2no(coll.find_le, probe)), repr(self.slow_find_le(num_list, probe)))
                    self.assertEquals(repr(self.ve2no(coll.find_lt, probe)), repr(self.slow_find_lt(num_list, probe)))
                    self.assertEquals(repr(self.ve2no(coll.find_ge, probe)), repr(self.slow_find_ge(num_list, probe)))
                    self.assertEquals(repr(self.ve2no(coll.find_gt, probe)), repr(self.slow_find_gt(num_list, probe)))
                for i, item in enumerate(num_list):
                    # test __getitem__
                    self.assertEquals(repr(item), repr(coll[i]))
                    # test __contains__ and __iter__
                    self.assertTrue(item in coll)
                    # test count()
                    self.assertEquals(num_list.count(item), coll.count(item))
                # test __len__
                self.assertEquals(len(coll), num_nums)
                # test __reversed__
                self.assertEquals(list(map(repr, reversed(coll))), list(map(repr, reversed(num_list))))
                # test copy()
                self.assertEquals(list(coll.copy()), list(coll))
                # test clear()
                coll.clear()
                self.assertEquals(len(coll), 0)

    def test_alphabetical(self):
        coll = SortedCollection('The quick Brown Fox jumped'.split(), key=str.lower)
        self.assertEquals(coll._keys, ['brown', 'fox', 'jumped', 'quick', 'the'])  # pylint: disable=W0212
        self.assertEquals(coll._items, ['Brown', 'Fox', 'jumped', 'quick', 'The'])  # pylint: disable=W0212
        self.assertEquals(coll._key, str.lower)  # pylint: disable=W0212
        self.assertEquals(repr(coll), "SortedCollection(['Brown', 'Fox', 'jumped', 'quick', 'The'], key=lower)")
        coll.key = str.upper
        self.assertEquals(coll._key, str.upper)  # pylint: disable=W0212
        self.assertEquals(len(coll), 5)
        self.assertEquals(list(reversed(coll)), ['The', 'quick', 'jumped', 'Fox', 'Brown'])
        for item in coll:
            self.assertTrue(item in coll)
        for i, item in enumerate(coll):
            self.assertEquals(item, coll[i])
        coll.insert('jUmPeD')
        coll.insert_right('QuIcK')
        self.assertEquals(coll._keys, ['BROWN', 'FOX', 'JUMPED', 'JUMPED', 'QUICK', 'QUICK', 'THE'])  # pylint: disable=W0212
        self.assertEquals(coll._items, ['Brown', 'Fox', 'jUmPeD', 'jumped', 'quick', 'QuIcK', 'The'])  # pylint: disable=W0212
        self.assertEquals(coll.find_le('JUMPED'), 'jumped', coll.find_le('JUMPED'))
        self.assertEquals(coll.find_ge('JUMPED'), 'jUmPeD')
        self.assertEquals(coll.find_le('GOAT'), 'Fox')
        self.assertEquals(coll.find_ge('GOAT'), 'jUmPeD')
        self.assertEquals(coll.find('FOX'), 'Fox')
        self.assertEquals(coll[3], 'jumped')
        self.assertEquals(coll[3:5], ['jumped', 'quick'])
        self.assertEquals(coll[-2], 'QuIcK')
        self.assertEquals(coll[-4:-2], ['jumped', 'quick'])
        for i, item in enumerate(coll):
            self.assertEquals(coll.index(item), i)
        with self.assertRaises(ValueError):
            coll.index('xyzpdq')
        coll.remove('jumped')
        self.assertEquals(list(coll), ['Brown', 'Fox', 'jUmPeD', 'quick', 'QuIcK', 'The'])

    def test_list_of_dicts(self):
        things = [
            {'filename': 'hit.wav', 'length': 14002, 'style': 'modern'},
            {'filename': 'doc.rst', 'length': 491238, 'info': 'git'},
            {'filename': 'sample.py', 'length': 392, 'prog': 'sort'},
            {'filename': 'manifesto.txt', 'length': 8192, 'style': 'earnest'},
        ]
        another_thing = {'filename': 'eagle_swooping.png', 'length': 128000, 'symbol': True}
        coll = SortedCollection(key=itemgetter('filename'))
        # Fill the collection.
        for thing in things:
            coll.insert(thing)
        # Ensure things are sorted as expected.
        self.assertEquals(coll[3]['filename'], 'sample.py')
        self.assertEquals(coll.index(things[0]), 1)
        # Count an existing and non-existing item.
        self.assertEquals(coll.count(things[3]), 1)
        self.assertEquals(coll.count({'filename': 'not_present.txt'}), 0)
        # Test find_lt.
        self.assertEquals(coll.find_lt('sample.py')['filename'], 'manifesto.txt')
        coll_copy = copy(coll)
        # Insert another item, make sure it's present and ordered.
        coll.insert(another_thing)
        self.assertEquals(coll.find('eagle_swooping.png'), another_thing)
        self.assertEquals(coll[1]['filename'], 'eagle_swooping.png')
        item, idx = coll.find_with_index('eagle_swooping.png')
        self.assertEquals(item, another_thing)
        self.assertEquals(idx, 1)
        # Remove the added item - ensure that everything is as it was before insertion.
        self.assertNotEqual(len(coll), len(coll_copy))
        coll.remove(another_thing)
        self.assertNotEqual(coll[1]['filename'], 'eagle_swooping.png')
        for i in range(len(coll)):
            self.assertEquals(coll[i], coll_copy[i])
        # Ensure that replacement of item with a different key raises.
        with self.assertRaises(ValueError):
            coll.replace(0, another_thing)
        # Replace an item for real and ensure it was replaced.
        self.assertEquals(coll[0]['length'], 491238)
        coll.replace(0, {'filename': 'doc.rst', 'length': 14, 'useful': False})
        self.assertEquals(coll[0]['length'], 14)
        # find_with_index, remove
        # Ensure an empty collection works.
        coll2 = SortedCollection([], key=itemgetter('filename'))
        self.assertEquals(coll2.count({'filename': 'not_present.txt'}), 0)
