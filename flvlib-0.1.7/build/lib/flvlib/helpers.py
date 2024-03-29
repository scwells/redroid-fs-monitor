import time
import datetime

from StringIO import StringIO
from UserDict import DictMixin

class LocalTimezone(datetime.tzinfo):
    """A tzinfo class representing the system's idea of the local timezone"""
    STDOFFSET = datetime.timedelta(seconds=-time.timezone)
    if time.daylight:
        DSTOFFSET = datetime.timedelta(seconds=-time.altzone)
    else:
        DSTOFFSET = STDOFFSET
    DSTDIFF = DSTOFFSET - STDOFFSET
    ZERO = datetime.timedelta(0)

    def utcoffset(self, dt):
        if self._isdst(dt):
            return self.DSTOFFSET
        else:
            return self.STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return self.DSTDIFF
        else:
            return self.ZERO

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, -1)
        return time.localtime(time.mktime(tt)).tm_isdst > 0

Local = LocalTimezone()

class FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = datetime.timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return datetime.timedelta(0)

    def __eq__(self, other):
        try:
            return (self.__offset == other.__offset and
                    self.__name == other.__name)
        except AttributeError:
            return False

    def __repr__(self):
        return '<FixedOffset %s>' % self.__offset

class OrderedAttrDict(DictMixin):
    """
    A dictionary that preserves insert order and also has an attribute
    interface.

    Values can be transparently accessed and set as keys or as attributes.
    """

    def __init__(self, dict=None, **kwargs):
        self.__dict__["_order_priv_"] = []
        self.__dict__["_data_priv_"] = {}
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)

    # Mapping interface

    def __setitem__(self, key, value):
        if key not in self:
            self._order_priv_.append(key)
        self._data_priv_[key] = value

    def __getitem__(self, key):
        return self._data_priv_[key]

    def __delitem__(self, key):
        del self._data_priv_[key]
        self._order_priv_.remove(key)

    def keys(self):
        return list(self._order_priv_)

    # Attribute interface

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)

    # Equality
    def __eq__(self, other):
        try:
            my_iter = self.iteritems()
            his_iter = other.iteritems()
        except AttributeError:
            return False
        my_empty = False
        his_empty = False
        while True:
            try:
                my_key, my_val = my_iter.next()
            except StopIteration:
                my_empty = True
            try:
                his_key, his_val = his_iter.next()
            except StopIteration:
                his_empty = True
            if my_empty and his_empty:
                return True
            if my_empty or his_empty:
                return False
            if (my_key, my_val) != (his_key, his_val):
                return False

    # String representation
    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self)

    def __str__(self):
        return '{' + ', '.join([('%r: %r' % (key, self[key]))
                                for key in self._order_priv_]) + '}'


class ASPrettyPrinter(object):
    """Pretty printing of AS objects"""

    def pformat(cls, val, indent=0):
        cls.io = StringIO()
        cls.pprint_lookup(val, indent)
        return cls.io.getvalue()
    pformat = classmethod(pformat)

    def pprint(cls, val):
        print cls.pformat(val)
    pprint = classmethod(pprint)

    def pprint_lookup(cls, val, ident):
        if isinstance(val, basestring):
            return cls.pprint_string(val)
        if isinstance(val, (int, long, float)):
            return cls.pprint_number(val)
        if hasattr(val, 'iterkeys'):
            # dict interface
            return cls.pprint_dict(val, ident)
        if hasattr(val, 'append'):
            # list interface
            return cls.pprint_list(val, ident)
        # Unknown type ?
        cls.io.write("%r" % (val, ))
        return False
    pprint_lookup = classmethod(pprint_lookup)

    def pprint_string(cls, val):
        if isinstance(val, unicode):
            cls.io.write("u'%s'" % val.encode("UTF8"))
        else:
            cls.io.write("'%s'" % val)
        return False
    pprint_string = classmethod(pprint_string)

    def pprint_number(cls, val):
        cls.io.write(str(val))
        return False
    pprint_number = classmethod(pprint_number)

    def pprint_dict(cls, val, indent):

        def pprint_item(k):
            last_pos = cls.io.tell()
            cls.io.write(repr(k))
            cls.io.write(": ")
            new_indent = indent + cls.io.tell() - last_pos + 1
            return cls.pprint_lookup(val[k], new_indent)

        cls.io.write('{')
        indented = False
        keys = list(val.iterkeys())
        if keys:
            for k in keys[:-1]:
                indented |= pprint_item(k)
                cls.io.write(",\n%s " % (" "*indent))
            indented |= pprint_item(keys[-1])
        cls.io.write('}')
        return (len(keys) > 1) | indented
    pprint_dict = classmethod(pprint_dict)

    def pprint_list(cls, val, indent):
        last_pos = cls.io.tell()
        cls.io.write('[')
        new_indent = indent + cls.io.tell() - last_pos
        indented = False
        values = list(iter(val))
        if values:
            for v in values[:-1]:
                indented |= cls.pprint_lookup(v, new_indent)
                cls.io.write(",\n%s" % (" "*new_indent))
            indented |= cls.pprint_lookup(values[-1], new_indent)
        cls.io.write(']')
        return (len(values) > 1) | indented
    pprint_list = classmethod(pprint_list)

pformat = ASPrettyPrinter.pformat
pprint = ASPrettyPrinter.pprint
