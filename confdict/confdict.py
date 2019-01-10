# standard libs
from collections.abc import Mapping, MutableMapping
from copy import copy
import re

# third party libs

# project imports


class RecursiveDict(MutableMapping):
  def __init__(self, *args, **kwargs):
    self.root = kwargs.pop('__root', None)
    self.parent = kwargs.pop('__parent', None)
    self.key = kwargs.pop('__key', None)
    if self.parent is None:
      self.root = self
    self.store = dict()
    self.update(dict(*args, **kwargs))

  def key_to_path(self, key):
    if isinstance(key, list):
      return key
    else:
      return [ key ]

  def path_to_key(self, path):
    return path

  def __getitem__(self, key):
    path = self.key_to_path(copy(key))
    if len(path) == 1:
      current_key = path.pop(0)
      if current_key == '.':
        return self
      elif current_key == '..':
        return self.parent
      elif current_key == '...':
        return self.root
      else:
        return self.store[current_key]
    else:
      return self[path.pop(0)][path]

  def __setitem__(self, key, value):
    path = self.key_to_path(copy(key))
    if len(path) == 1:
      if isinstance(value, Mapping):
        current_key = path.pop(0)
        self.store[current_key] = self.__class__(__root=self.root,
                                                 __parent=self,
                                                 __key=current_key,
                                                 **value)
      else:
        self.store[path.pop(0)] = value
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
          if isinstance(inner_key, list):
            yield self.path_to_key([ key ] + inner_key)
          else:
            yield self.path_to_key([ key, inner_key ])
      else:
        yield self.path_to_key([ key ])

  def __len__(self):
    return sum(1 for _ in self)

  def __str__(self):
    return str(self.__class__.__name__) + " " + str(self.to_dict())

  def __unicode__(self):
    return str(self).encode('utf-8')

  def __repr__(self):
    return str(self)

  def update(self, d):
    for k, v in d.items():
      path = self.key_to_path(copy(k))
      if isinstance(v, Mapping) and k in self:
        self[k].update(v)
      else:
        self[k] = v

  def to_dict(self):
    d = {}
    for key in self:
      path = self.key_to_path(copy(key))
      value = self[path]
      d[key] = value
    return d


class FallbackDict(RecursiveDict):
  pass

class DictWithFallback(RecursiveDict):
  def __init__(self, *args, **kwargs):
    self.fallback = FallbackDict(**kwargs.pop('fallback', {}))
    super(DictWithFallback, self).__init__(*args, **kwargs)

  def __getitem__(self, key):
    try:
      return super(DictWithFallback, self).__getitem__(key)
    except KeyError as e:
      path = self.key_to_path(copy(key))
      print(self.fallback)
      print(path)
      if len(path) == 1:
        return self.fallback
      else:
        key = self.path_to_key(path[1:])
        return self.fallback[key]

class ConfDict(DictWithFallback):
  def __init__(self, *args, **kwargs):
    self.separator = kwargs.pop('_separator', '/')
    self.interpolation_regex = re.compile(kwargs.pop('_interpolation_regex', r'{{([^{}]*)}}'))
    super(ConfDict, self).__init__(*args, **kwargs)

  def key_to_path(self, key):
    if isinstance(key, str) and self.separator in key:
      return key.split(self.separator)
    else:
      return super(ConfDict, self).key_to_path(key)

  def path_to_key(self, path):
    if isinstance(path, list):
      return self.separator.join(path)
    else:
      return super(ConfDict, self).path_to_key(path)

  def __getitem__(self, key):
    value = super(ConfDict, self).__getitem__(key)
    if isinstance(value, str):
      return self.interpolate_value(value)
    else:
      return value

  def interpolate_value(self, value):
    blocks = self.interpolation_regex.findall(value)
    interpolated_value = value
    for block in blocks:
      if block in self:
        interpolated_value = interpolated_value.replace('{{' + block + '}}', self[block])

    return interpolated_value