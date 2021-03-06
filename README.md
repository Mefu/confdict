# ConfDict

[![Build Status](https://travis-ci.org/Mefu/confdict.svg?branch=master)](https://travis-ci.org/Mefu/confdict)
[![PyPI version](https://img.shields.io/pypi/v/confdict.svg)](https://pypi.org/project/confdict/)
[![Python versions](https://img.shields.io/pypi/pyversions/confdict.svg)](https://pypi.org/project/confdict/)

Configuration dictionary that extends built-in python dict with recursive access, self references and fallback functionality. There is no extensive documentation yet, you can check out tests to figure out all features.

## Example usage.

```python
>>> from confdict import ConfDict
>>> cd = ConfDict(
  # Configuration of ConfDict, these are default values
  __separator = '/',
  __self_key = '.',
  __parent_key = '..',
  __root_key = '...',
  __key_key = '<key>',
  __interpolation_regex = r'({{([^{}]*)}})',
  __fallback_key = 'fallback',

  # Remaining arguments will directly be stored in underlying dict
  users = {
    # fallback dict is used when a key is not found at that level
    'fallback': {
      # <key> is evaluated to key of the current level
      # it is useful when used with fallback
      'username': '{{<key>}}',
      # you can use self references
      'ssh_private_key': '/home/{{username}}/.ssh/id_rsa',
    },
  }
)
>>> cd
ConfDict
{ 'users': { 'fallback': { 'ssh_private_key': '/home/{{username}}/.ssh/id_rsa',
                           'username': '{{<key>}}'}}}
>>> cd['users/john/username']
'john'
>>> cd['users/john/ssh_private_key']
'/home/john/.ssh/id_rsa'
>>> cd['users/john']
ConfDict
{'ssh_private_key': '/home/john/.ssh/id_rsa', 'username': 'john'}
>>> cd['users/jean']
ConfDict
{'ssh_private_key': '/home/jean/.ssh/id_rsa', 'username': 'jean'}
>>> cd['users/jean'] = { 'username': 'jeans_custom_username' }
>>> cd['users/jean/ssh_private_key']
'/home/jeans_custom_username/.ssh/id_rsa'
>>> # 'jean' exists now under 'users'
>>> # there is no partial fallback so there is no 'ssh_private_key'
>>> cd['users/jean']
ConfDict
{'username': 'jeans_custom_username'}
>>> # we can realize fallback as jean to make concrete values
>>> cd['users/fallback'].realize('jean')
>>> cd['users/jean']
ConfDict
{'ssh_private_key': '/home/jeans_custom_username/.ssh/id_rsa', 'username': 'jeans_custom_username'}
>>> # interpolation still works
>>> cd['users/jean/username'] = 'jeans_custom_username2'
>>> cd['users/jean/ssh_private_key']
'/home/jeans_custom_username2/.ssh/id_rsa'
```


## Installation
```
$ pip install confdict
```

## Development

There is a `Makefile` to automate commonly used development tasks.

### Environment Setup

```
### create a virtualenv for development

$ sudo pip install virtualenv # or your preferred way to install virtualenv

$ make virtualenv # will also install dependencies

$ source env/bin/activate

### run pytest / coverage

$ make test

### before commit

$ make format
```
