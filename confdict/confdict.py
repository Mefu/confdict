# standard libs
from collections.abc import Mapping, MutableMapping
from copy import copy
import re

# third party libs

# project imports


class RecursiveDict(MutableMapping):
  def __init__(self, *args, **kwargs):
    self.separator = kwargs.pop('__separator', '/')
    self.self_key = kwargs.pop('__self_key', '.')
    self.parent_key = kwargs.pop('__parent_key', '..')
    self.root_key = kwargs.pop('__root_key', '...')
    self.key_key = kwargs.pop('__key_key', '<key>')
    self.builtin_keys = [
      self.self_key, self.parent_key, self.root_key, self.key_key
    ]

    self.root = kwargs.pop('__root', None)
    self.parent = kwargs.pop('__parent', None)
    self.key = kwargs.pop('__key', None)
    if self.parent is None:
      self.root = self
    self.store = dict()
    self.update(dict(*args, **kwargs))

  def key_to_path(self, key):
    if isinstance(key, str) and self.separator in key:
      return key.split(self.separator)
    elif isinstance(key, list):
      return key
    else:
      return [ key ]

  def path_to_key(self, path):
    assert type(path) == list
    return self.separator.join(path)

  def __getitem__(self, key):
    path = self.key_to_path(copy(key))
    if len(path) == 1:
      current_key = path.pop(0)
      if current_key == self.self_key:
        return self
      elif current_key == self.parent_key and self.parent:
        return self.parent
      elif current_key == self.root_key:
        return self.root
      elif current_key == self.key_key:
        return self.key
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

  def __unicode__(self):
    return str(self.__class__.__name__) + " " + str(self.to_dict())

  def __repr__(self):
    return self.__unicode__()

  def update(self, d):
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
  def __init__(self, *args, **kwargs):
    self.interpolation_regex = re.compile(kwargs.pop('__interpolation_regex', r'{{([^{}]*)}}'))
    super(InterpolatedDict, self).__init__(*args, **kwargs)

  def __getitem__(self, key):
    value = super(InterpolatedDict, self).__getitem__(key)
    if isinstance(value, str):
      return self.interpolate_value(value)
    else:
      return value

  def interpolate_value(self, value):
    blocks = self.interpolation_regex.findall(value)
    interpolated_value = value
    for block in blocks:
      if block in self or block == self.key_key:
        interpolated_value = interpolated_value.replace('{{' + block + '}}', self[block])

    return interpolated_value


class ConfDict(InterpolatedDict):
  def __init__(self, *args, **kwargs):
    self.fallback = kwargs.pop('fallback', None)
    super(ConfDict, self).__init__(*args, **kwargs)

    if self.fallback:
      self.fallback = ConfDict(__root=self.root, __parent=self, __key='fallback', **self.fallback)

    self.fallback_enabled = True

  def __getitem__(self, key):
    try:
      if key == 'fallback':
        self.fallback.key = 'fallback'
        return self.fallback
      else:
        return super(ConfDict, self).__getitem__(key)
    except KeyError as e:
      path = self.key_to_path(copy(key))
      if self.fallback_enabled:
        if len(path) == 1 and self.fallback:
          self.fallback.key = path[0]
          return self.fallback
        elif self.fallback:
          self.fallback.key = path[0]
          remaining_path = self.path_to_key(path[1:])
          return self.fallback[remaining_path]
        elif self.parent and self.parent.fallback:
          self.parent.fallback.key = self.key
          return self.parent.fallback[path]
      raise e

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

