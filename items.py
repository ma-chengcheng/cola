from abc import ABCMeta
import six
from collections import MutableMapping


class BaseItem(object):
    pass


class Field(dict):
    """元字段"""


class ItemMeta(ABCMeta):
    """定义抽象基类 可执行类的强制检查 并确保子类实现特定方法 不能直接被实例化"""

    def __new__(mcs, class_name, bases, attrs):
        classcell = attrs.pop('__classcell__', None)
        new_bases = tuple(base._class for base in bases if hasattr(base, '_class'))
        _class = super(ItemMeta, mcs).__new__(mcs, 'x_' + class_name, new_bases, attrs)

        fields = getattr(_class, 'fields', {})
        new_attrs = {}
        for n in dir(_class):
            v = getattr(_class, n)
            if isinstance(v, Field):
                fields[n] = v
            elif n in attrs:
                new_attrs[n] = attrs[n]

        new_attrs['fields'] = fields
        new_attrs['_class'] = _class
        if classcell is not None:
            new_attrs['__classcell__'] = classcell
        return super(ItemMeta, mcs).__new__(mcs, class_name, bases, new_attrs)


class DictItem(MutableMapping, BaseItem):

    """
    https://github.com/scrapy/scrapy/blob/master/scrapy/item.py
    """

    fields = {}

    def __init__(self, *args, **kwargs):
        self._values = {}
        if args or kwargs:
            for k, v in six.iteritems(dict(*args, **kwargs)):
                self[k] = v

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, value):
        if key in self.fields:
            self._values[key] = value
        else:
            raise KeyError("{} does not set this field: {}".format(self.__class__.__name__, key))

    def __delitem__(self, key):
        del self._values[key]

    def __getattr__(self, item):
        if item in self.fields:
            raise AttributeError('Use item[{}] to get field value'.format(item))
        raise AttributeError(item)

    def __len__(self):
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def keys(self):
        return self._values.keys()


@six.add_metaclass(ItemMeta)
class Item(DictItem):
    pass


class ReviewItem(Item):
    content = Field()
    rating = Field()
    data = Field()
    name = Field()
    place = Field()
    age = Field()
    sex = Field()
    join_data = Field()
    review_time = Field()
    review_rating = Field()
