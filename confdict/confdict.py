# standard libs
from collections.abc import Mapping, MutableMapping
from copy import copy
import re

# third party libs

# project imports


class RecursiveDict(MutableMapping):
  """A dictionary that allows recursive and relative access to its contents."""
  def __init__(self, *args, **kwargs):
    # recursive structure
    self.root = kwargs.pop('__root', None)
    self.parent = kwargs.pop('__parent', None)
    self.key = kwargs.pop('__key', None)
    if self.parent is None:
      self.root = self

    # keys and chars used for various functionalities
    # defaults
    self.config = {
      'separator': '/',
      'self_key': '.',
      'parent_key': '..',
      'root_key': '...',
      'key_key': '<key>',
    }

    # from parent
    if self.parent:
      self.config.update(self.parent.config)

    # from kwargs
    if '__separator' in kwargs:
      self.config['separator'] = kwargs['__separator']
    if '__self_key' in kwargs:
      self.config['self_key'] = kwargs['__self_key']
    if '__parent_key' in kwargs:
      self.config['parent_key'] = kwargs['__parent_key']
    if '__root_key' in kwargs:
      self.config['root_key'] = kwargs['__root_key']
    if '__key_key' in kwargs:
      self.config['key_key'] = kwargs['__key_key']

    self.builtin_keys = [
      self.config['self_key'],
      self.config['parent_key'],
      self.config['root_key'],
      self.config['key_key'],
    ]

    # underlying storage
    self.store = dict()
    self.update(dict(*args, **kwargs))

  def key_to_path(self, key):
    """
    Function that transforms key to list of keys aka path.
    By default, separates key using `separator` if it is string.
    Must return `list`, cannot assume type of `key`.
    """
    if isinstance(key, str) and self.config['separator'] in key:
      return key.split(self.config['separator'])
    elif isinstance(key, list):
      return key
    else:
      return [ key ]

  def path_to_key(self, path):
    """
    Function that will transform a path into single key.
    By default, it will join all elements using `separator`.
    Type of path is guaranteed to be a `list`.
    """
    assert type(path) == list
    return self.config['separator'].join(path)

  def key_before_get(self, key):
    return key

  def key_before_set(self, key):
    return key

  def value_before_set(self, value):
    return value

  def value_after_get(self, value):
    return value

  def key_not_found(self, key, error):
    raise error

  def __getitem__(self, key):
    """
    Transforms key to path and tries to recursively descent into dict.
    It will also handle relative keys, eg `..` and `...`.
    """
    path = self.key_to_path(copy(key))

    if len(path) == 1:
      current_key = path.pop(0)
      current_key = self.key_before_get(current_key)
      if current_key == self.config['self_key']:
        return self
      elif current_key == self.config['parent_key'] and self.parent:
        return self.parent
      elif current_key == self.config['root_key']:
        return self.root
      elif current_key == self.config['key_key']:
        return self.key
      else:
        try:
          value = self.store[current_key]
        except KeyError as e:
          value = self.key_not_found(current_key, e)

        value = self.value_after_get(value)
        return value
    else:
      return self[path.pop(0)][path]

  def __setitem__(self, key, value):
    path = self.key_to_path(copy(key))
    if len(path) == 1:
      current_key = path.pop(0)
      current_key = self.key_before_set(current_key)
      if isinstance(value, Mapping):
        self.store[current_key] = self.__class__(__root=self.root,
                                                 __parent=self,
                                                 __key=current_key,
                                                 **value)
      else:
        value = self.value_before_set(value)
        self.store[current_key] = value
    else:
      self[path.pop(0)][path] = value

  def __delitem__(self, key):
    path = self.key_to_path(copy(key))
    if len(path) == 1:
      del self.store[path.pop(0)]
    else:
      del self[path.pop(0)][path]

  def __contains__(self, key):
    path = self.key_to_path(copy(key))
    if len(path) == 1:
      return path.pop(0) in self.store
    else:
      return self[path.pop(0)].__contains__(path)

  def __iter__(self):
    for key in self.store:
      value = self.store[key]
      if isinstance(value, Mapping):
        for inner_key in value:
          yield self.path_to_key([ key, inner_key ])
      else:
        yield self.path_to_key([ key ])

  def __len__(self):
    return sum(1 for _ in self)

  def __unicode__(self):
    return str(self.__class__.__name__) + " " + str(self.to_dict())

  def __repr__(self):
    return self.__unicode__()

  def update(self, d):
    """
    Default update method of this dictionary is a deep update.
    """
    for k, v in d.items():
      path = self.key_to_path(copy(k))
      if isinstance(v, Mapping) and k in self:
        self[k].update(v)
      else:
        self[k] = v

  def to_dict(self):
    d = {}
    for key in self.store:
      value = self[key]
      if isinstance(value, RecursiveDict):
        d[key] = value.to_dict()
      else:
        d[key] = value
    return d


class InterpolatedDict(RecursiveDict):
  """
  Enables self referential values on top of RecursiveDict.
  By default, it will try to evaluate values containing double curly braces.
  It will also evaluate "<key>" to key of current dictionary level.
  """
  def __init__(self, *args, **kwargs):
    interpolation_regex = kwargs.pop('__interpolation_regex', None)
    super(InterpolatedDict, self).__init__(*args, **kwargs)
    if interpolation_regex is not None:
      self.config['interpolation_regex'] = re.compile(interpolation_regex)
    elif 'interpolation_regex' not in self.config:
      self.config['interpolation_regex'] = re.compile(r'{{([^{}]*)}}')

  def value_after_get(self, value):
    if isinstance(value, str):
      return self.interpolate_value(value)
    else:
      return super(InterpolatedDict, self).value_after_get(value)

  def interpolate_value(self, value):
    if self.key == 'fallback':
      return value

    blocks = self.config['interpolation_regex'].findall(value)
    interpolated_value = value
    for block in blocks:
      if block in self or block == self.config['key_key']:
        interpolated_value = interpolated_value.replace('{{' + block + '}}', self[block])

    return interpolated_value

class ConfDict(InterpolatedDict):
  """
  Adds fallback functionality on top of InterpolatedDict. If current level does
  not contain the key and contains a fallback, this dict will fall back to that
  dictionary with remaining path. If this level does not contain a fallback it
  will try to fallback to parents fallback until it reaches root level.
  """
  def __init__(self, *args, **kwargs):
    self.fallback = kwargs.pop('fallback', None)
    is_fallback = kwargs.pop('__is_fallback', None)
    super(ConfDict, self).__init__(*args, **kwargs)

    if self.fallback:
      self.fallback = ConfDict(__root=self.root,
                               __parent=self,
                               __key='fallback',
                               __is_fallback=True,
                               **self.fallback)

    if is_fallback is not None:
      self.config['is_fallback'] = is_fallback
    elif 'is_fallback' not in self.config:
      self.config['is_fallback'] = False

    self.fallback_enabled = True

  def key_not_found(self, key, error):
    print("-" * 80)
    print("WTF1")
    print(self.root)
    print(self.store)
    print("WTF2")
    print(self.config['is_fallback'])
    print("WTF3")
    print(key)
    print("WTF4")
    print("-" * 80)
    if key == 'fallback':
      return self.fallback
    else:
      if self.fallback_enabled:
        return self.parent[self.config['separator'].join(['fallback', key])]


    return super(ConfDict, self).key_not_found(key, error)

  def __setitem__(self, key, value):
    self.fallback_enabled = False
    super(ConfDict, self).__setitem__(key, value)
    self.fallback_enabled = True

  def __delitem__(self, key):
    self.fallback_enabled = False
    super(ConfDict, self).__delitem__(key)
    self.fallback_enabled = True

  def __contains__(self, key):
    self.fallback_enabled = False
    res = super(ConfDict, self).__contains__(key)
    self.fallback_enabled = True
    return res

  def update(self, d):
    dcopy = copy(d)
    if 'fallback' in dcopy:
      if self.fallback:
        self.fallback.update(dcopy.pop('fallback'))
      else:
        self.fallback = ConfDict(**dcopy.pop('fallback'))
    super(ConfDict, self).update(dcopy)

  def to_dict(self):
    d = super(ConfDict, self).to_dict()
    if self.fallback:
      self.fallback.key = 'fallback'
      d['fallback'] = self.fallback.to_dict()
    return d

