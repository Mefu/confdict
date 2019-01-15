# ConfDict

Configuration dictionary that extends built-in python dict with recursive access, fallback functionality and self references.

Example usage of all of its extra features are as follows.

```
>>> from confdict import ConfDict
>>> cd = ConfDict(
  # Configuration of ConfDict, you can omit them if you are fine with these
  __separator = '/',
  __self_key = '.',
  __parent_key = '..',
  __root_key = '...',
  __key_key = '<key>',
  __interpolation_regex = r'{{([^{}]*)}}',

  # You can give dict contents directly to constructor as keyword arguments
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
ConfDict {'users': {'fallback': {'username': 'fallback', 'ssh_private_key': '/home/fallback/.ssh/id_rsa'}}}
>>> cd['users/john/username']
'john'
>>> cd['users/john/ssh_private_key']
'/home/john/.ssh/id_rsa'
>>> cd['users/jean'] = { 'username': 'jeans_custom_username' }
>>> cd['users/jean/ssh_private_key']
'/home/jeans_custom_username/.ssh/id_rsa'
```


## Installation
```
$ pip install
```

## Development

This project includes a number of helpers in the `Makefile` to streamline common development tasks.

### Environment Setup

```
### create a virtualenv for development

$ sudo pip install virtualenv # or your preferred way to install virtualenv

$ make virtualenv

$ source env/bin/activate

### run pytest / coverage

$ make test
```
