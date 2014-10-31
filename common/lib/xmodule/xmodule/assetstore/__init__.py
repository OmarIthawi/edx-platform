"""
Classes representing asset & asset thumbnail metadata.
"""

from datetime import datetime
import pytz
from contracts import contract, new_contract
from bisect import bisect_left, bisect_right
from opaque_keys.edx.keys import CourseKey, AssetKey

new_contract('AssetKey', AssetKey)
new_contract('datetime', datetime)
new_contract('basestring', basestring)


class IncorrectAssetIdType(Exception):
    """
    Raised when the asset ID passed-in to create an AssetMetadata or
    AssetThumbnailMetadata is of the wrong type.
    """
    pass


class SortedCollection(object):
    '''Sequence sorted by a key function.

    http://code.activestate.com/recipes/577197-sortedcollection/

    SortedCollection() is much easier to work with than using bisect() directly.
    It supports key functions like those use in sorted(), min(), and max().
    The result of the key function call is saved so that keys can be searched
    efficiently.

    Instead of returning an insertion-point which can be hard to interpret, the
    five find-methods return a specific item in the sequence. They can scan for
    exact matches, the last item less-than-or-equal to a key, or the first item
    greater-than-or-equal to a key.

    Once found, an item's ordinal position can be located with the index() method.
    New items can be added with the insert() and insert_right() methods.
    Old items can be deleted with the remove() method.

    The usual sequence methods are provided to support indexing, slicing,
    length lookup, clearing, copying, forward and reverse iteration, contains
    checking, item counts, item removal, and a nice looking repr.

    Finding and indexing are O(log n) operations while iteration and insertion
    are O(n).  The initial sort is O(n log n).

    The key function is stored in the 'key' attibute for easy introspection or
    so that you can assign a new key function (triggering an automatic re-sort).

    In short, the class was designed to handle all of the common use cases for
    bisect but with a simpler API and support for key functions.

    >>> from pprint import pprint
    >>> from operator import itemgetter

    >>> s = SortedCollection(key=itemgetter(2))
    >>> for record in [
    ...         ('roger', 'young', 30),
    ...         ('angela', 'jones', 28),
    ...         ('bill', 'smith', 22),
    ...         ('david', 'thomas', 32)]:
    ...     s.insert(record)

    >>> pprint(list(s))         # show records sorted by age
    [('bill', 'smith', 22),
     ('angela', 'jones', 28),
     ('roger', 'young', 30),
     ('david', 'thomas', 32)]

    >>> s.find_le(29)           # find oldest person aged 29 or younger
    ('angela', 'jones', 28)
    >>> s.find_lt(28)           # find oldest person under 28
    ('bill', 'smith', 22)
    >>> s.find_gt(28)           # find youngest person over 28
    ('roger', 'young', 30)

    >>> r = s.find_ge(32)       # find youngest person aged 32 or older
    >>> s.index(r)              # get the index of their record
    3
    >>> s[3]                    # fetch the record at that index
    ('david', 'thomas', 32)

    >>> s.key = itemgetter(0)   # now sort by first name
    >>> pprint(list(s))
    [('angela', 'jones', 28),
     ('bill', 'smith', 22),
     ('david', 'thomas', 32),
     ('roger', 'young', 30)]

    '''

    def __init__(self, iterable=(), key=None):
        self._given_key = key
        key = (lambda x: x) if key is None else key
        decorated = sorted((key(item), item) for item in iterable)
        self._keys = [k for k, item in decorated]
        self._items = [item for k, item in decorated]
        self._key = key

    def _getkey(self):
        """
        Return the key.
        """
        return self._key

    def _setkey(self, key):
        """
        Set the key.
        """
        if key is not self._key:
            self.__init__(self._items, key=key)

    def _delkey(self):
        """
        Delete the key.
        """
        self._setkey(None)

    key = property(_getkey, _setkey, _delkey, 'key function')

    def clear(self):
        """
        Clear the collection.
        """
        self.__init__([], self._key)

    def copy(self):
        """
        Copy the collection.
        """
        return self.__class__(self, self._key)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __setitem__(self, i, item):
        raise NotImplementedError()

    def __delitem__(self, i):
        raise NotImplementedError()

    def __iter__(self):
        return iter(self._items)

    def __reversed__(self):
        return reversed(self._items)

    def __repr__(self):
        return '%s(%r, key=%s)' % (
            self.__class__.__name__,
            self._items,
            getattr(self._given_key, '__name__', repr(self._given_key))
        )

    def __reduce__(self):
        return self.__class__, (self._items, self._given_key)

    def __contains__(self, item):
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return item in self._items[i:j]

    def index(self, item):
        'Find the position of an item.  Raise ValueError if not found.'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].index(item) + i

    def count(self, item):
        'Return number of occurrences of item'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].count(item)

    def insert(self, item):
        'Insert a new item.  If equal keys are found, add to the left'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def replace(self, idx, item):
        'Replace an item at a particular index. Raise ValueError if keys are not equal.'
        k = self._key(item)
        if self._keys[idx] != k:
            raise ValueError('Key {} not equal to idx {} key {} for replace.'. format(k, idx, self._keys[idx]))
        self._items[idx] = item

    def insert_right(self, item):
        'Insert a new item.  If equal keys are found, add to the right'
        k = self._key(item)
        i = bisect_right(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)

    def remove(self, item):
        'Remove first occurence of item.  Raise ValueError if not found'
        i = self.index(item)
        del self._keys[i]
        del self._items[i]

    def find_with_index(self, k):
        'Return first item with a key == k and its index.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            return self._items[i], i
        raise ValueError('No item found with key equal to: %r' % (k,))

    def find(self, k):
        'Return first item with a key == k.  Raise ValueError if not found.'
        item, _ = self.find_with_index(k)
        return item

    def find_le(self, k):
        'Return last item with a key <= k.  Raise ValueError if not found.'
        i = bisect_right(self._keys, k)
        if i:
            return self._items[i - 1]
        raise ValueError('No item found with key at or below: %r' % (k,))

    def find_lt(self, k):
        'Return last item with a key < k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i:
            return self._items[i - 1]
        raise ValueError('No item found with key below: %r' % (k,))

    def find_ge(self, k):
        'Return first item with a key >= equal to k.  Raise ValueError if not found'
        i = bisect_left(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key at or above: %r' % (k,))

    def find_gt(self, k):
        'Return first item with a key > k.  Raise ValueError if not found'
        i = bisect_right(self._keys, k)
        if i != len(self):
            return self._items[i]
        raise ValueError('No item found with key above: %r' % (k,))


class AssetMetadata(object):
    """
    Stores the metadata associated with a particular course asset. The asset metadata gets stored
    in the modulestore.
    """

    TOP_LEVEL_ATTRS = ['basename', 'internal_name', 'locked', 'contenttype', 'md5']
    EDIT_INFO_ATTRS = ['curr_version', 'prev_version', 'edited_by', 'edited_on']
    ALLOWED_ATTRS = TOP_LEVEL_ATTRS + EDIT_INFO_ATTRS

    # All AssetMetadata objects should have AssetLocators with this type.
    ASSET_TYPE = 'asset'

    @contract(asset_id='AssetKey', basename='basestring|None', internal_name='basestring|None', locked='bool|None', contenttype='basestring|None',
              md5='basestring|None', curr_version='basestring|None', prev_version='basestring|None', edited_by='int|None', edited_on='datetime|None')
    def __init__(self, asset_id,
                 basename=None, internal_name=None,
                 locked=None, contenttype=None, md5=None,
                 curr_version=None, prev_version=None,
                 edited_by=None, edited_on=None, field_decorator=None):
        """
        Construct a AssetMetadata object.

        Arguments:
            asset_id (AssetKey): Key identifying this particular asset.
            basename (str): Original path to file at asset upload time.
            internal_name (str): Name under which the file is stored internally.
            locked (bool): If True, only course participants can access the asset.
            contenttype (str): MIME type of the asset.
            curr_version (str): Current version of the asset.
            prev_version (str): Previous version of the asset.
            edited_by (str): Username of last user to upload this asset.
            edited_on (datetime): Datetime of last upload of this asset.
            field_decorator (function): used by strip_key to convert OpaqueKeys to the app's understanding
        """
        if asset_id.asset_type != self.ASSET_TYPE:
            raise IncorrectAssetIdType()
        self.asset_id = asset_id if field_decorator is None else field_decorator(asset_id)
        self.basename = basename  # Path w/o filename.
        self.internal_name = internal_name
        self.locked = locked
        self.contenttype = contenttype
        self.md5 = md5
        self.curr_version = curr_version
        self.prev_version = prev_version
        self.edited_by = edited_by
        self.edited_on = edited_on or datetime.now(pytz.utc)

    def __repr__(self):
        return """AssetMetadata{!r}""".format((
            self.asset_id,
            self.basename, self.internal_name,
            self.locked, self.contenttype, self.md5,
            self.curr_version, self.prev_version,
            self.edited_by, self.edited_on
        ))

    def update(self, attr_dict):
        """
        Set the attributes on the metadata. Ignore all those outside the known fields.

        Arguments:
            attr_dict: Prop, val dictionary of all attributes to set.
        """
        for attr, val in attr_dict.iteritems():
            if attr in self.ALLOWED_ATTRS:
                setattr(self, attr, val)

    def to_mongo(self):
        """
        Converts metadata properties into a MongoDB-storable dict.
        """
        return {
            'filename': self.asset_id.path,
            'basename': self.basename,
            'internal_name': self.internal_name,
            'locked': self.locked,
            'contenttype': self.contenttype,
            'md5': self.md5,
            'curr_version': self.curr_version,
            'prev_version': self.prev_version,
            'edited_by': self.edited_by,
            'edited_on': self.edited_on
        }

    @contract(asset_doc='dict | None')
    def from_mongo(self, asset_doc):
        """
        Fill in all metadata fields from a MongoDB document.

        The asset_id prop is initialized upon construction only.
        """
        if asset_doc is None:
            return
        self.basename = asset_doc['basename']
        self.internal_name = asset_doc['internal_name']
        self.locked = asset_doc['locked']
        self.contenttype = asset_doc['contenttype']
        self.md5 = asset_doc['md5']
        self.curr_version = asset_doc['curr_version']
        self.prev_version = asset_doc['prev_version']
        self.edited_by = asset_doc['edited_by']
        self.edited_on = asset_doc['edited_on']


class AssetThumbnailMetadata(object):
    """
    Stores the metadata associated with the thumbnail of a course asset.
    """

    # All AssetThumbnailMetadata objects should have AssetLocators with this type.
    ASSET_TYPE = 'thumbnail'

    @contract(asset_id='AssetKey', internal_name='str | unicode | None')
    def __init__(self, asset_id, internal_name=None, field_decorator=None):
        """
        Construct a AssetThumbnailMetadata object.

        Arguments:
            asset_id (AssetKey): Key identifying this particular asset.
            internal_name (str): Name under which the file is stored internally.
        """
        if asset_id.asset_type != self.ASSET_TYPE:
            raise IncorrectAssetIdType()
        self.asset_id = asset_id if field_decorator is None else field_decorator(asset_id)
        self.internal_name = internal_name

    def __repr__(self):
        return """AssetMetadata{!r}""".format((self.asset_id, self.internal_name))

    def to_mongo(self):
        """
        Converts metadata properties into a MongoDB-storable dict.
        """
        return {
            'filename': self.asset_id.path,
            'internal_name': self.internal_name
        }

    @contract(thumbnail_doc='dict | None')
    def from_mongo(self, thumbnail_doc):
        """
        Fill in all metadata fields from a MongoDB document.

        The asset_id prop is initialized upon construction only.
        """
        if thumbnail_doc is None:
            return
        self.internal_name = thumbnail_doc['internal_name']
