# standard libs
from textwrap import dedent

# third party libs
import pytest

# project imports
from confdict import ConfDict


def test_get():
  cd = ConfDict(
    k1='v1',
    k2={
      'k21': 'v21',
      'k22': {
        'k222': 'v222',
      },
    },
    k3={
      'k31': 'v31',
      'k32': 'v32',
    },
  )

  assert cd['k1'] == 'v1'
  assert cd['k2/k22/k222'] == 'v222'
  assert cd['k2']['k22/k222'] == 'v222'
  assert cd['k2']['k22']['k222'] == 'v222'
  assert cd['k3'] == {
    'k31': 'v31',
    'k32': 'v32',
  }

  assert cd['.'] == cd
  assert cd['k2/..'] == cd
  assert cd['k2/k22/...'] == cd
  assert cd['k2/k22/../k21'] == cd['k2/k21']
  assert cd['k2/../../../k1'] == cd['k1']
  assert cd['k2/<key>'] == 'k2'


def test_set():
  cd = ConfDict(
    k1='v1',
    k2={
      'k22': {
        'k222': 'v222',
      },
    },
    k3={
      'k31': 'v31',
      'k32': 'v32',
    },
  )

  cd['k1'] = 'v1_2'
  assert cd['k1'] == 'v1_2'

  cd['k2/k22/k222'] = 'v222_2'
  assert cd['k2/k22/k222'] == 'v222_2'

  cd['k2']['k22']['k222'] = 'v222_3'
  assert cd['k2/k22/k222'] == 'v222_3'

  cd['k2/k22/../k21'] = 'v21'
  assert cd['k2/k22/../k21'] == 'v21'


def test_delete():
  cd = ConfDict(
    k1='v1',
    k2={
      'k22': {
        'k221': 'v221',
        'k222': 'v222',
      },
    },
    k3={
      'k31': 'v31',
      'k32': 'v32',
    },
  )

  del cd['k2/k22/k222']
  with pytest.raises(KeyError):
    cd['k2/k22/k222']

  del cd['k3']
  with pytest.raises(KeyError):
    cd['k3/k31']
  with pytest.raises(KeyError):
    cd['k3/k32']


def test_update():
  cd = ConfDict(
    k1={
      'k11': 'v11',
      'k12': 'v12',
    },
  )

  cd.update({
    'k1': {
      'k12': 'v12_2',
      'k13': 'v13'
    },
  })
  assert cd['k1/k11'] == 'v11'
  assert cd['k1/k12'] == 'v12_2'
  assert cd['k1/k13'] == 'v13'


def test_contains():
  cd = ConfDict(
    k1={
      'k11': 'v11',
      'k12': {
        'k121': 'v121',
      },
    },
  )

  assert 'k1' in cd
  assert 'k1/k12' in cd
  assert 'k1/k12/..' in cd
  assert '<key>' in cd


def test_interpolation_get():
  cd = ConfDict(
    k1={
      'k11': 'v11',
    },
    k2={
      'k21': '{{.../k1/k11}}',
      'k22': {
        'k221': '{{./k222}}',
        'k222': '{{../k23}}',
        'k223': '{{<key>}}',
      },
      'k23': 'v23',
      'k24': '{{k22}}'
    },
  )

  assert cd['k1/k11'] == 'v11'
  assert cd['k2/k22/k221'] == 'v23'
  assert cd['k2/k22/k222'] == 'v23'
  assert cd['k2/k22/k223'] == 'k22'
  assert cd['k2/k24/k221'] == 'v23'
  assert cd['k2/k24/k222'] == 'v23'
  assert cd['k2/k24/k223'] == 'k22'


def test_interpolation_set():
  cd = ConfDict(k1={'k11': 'v11', 'k12': '{{k11}}'}, )

  cd['k1/k11'] = 'v11_2'
  assert cd['k1/k12'] == 'v11_2'


def test_interpolation_delete():
  cd = ConfDict(k1={'k11': 'v11', 'k12': '{{k11}}'}, )

  del cd['k1/k11']
  with pytest.raises(KeyError):
    cd['k1/k12']


def test_fallback_get():
  cd = ConfDict(
    k1={
      'fallback': {
        'k111': 'v111f',
        'k112': {
          'k1121': 'v1121f',
          'k1122': 'v1122f',
        },
        'k113': 'v113f',
      },
      'k11': {
        'k111': 'v111',
        'k112': {
          'k1121': 'v1121',
        },
        'k113': 'v113',
      },
    },
  )

  assert cd['k1/k11/k111'] == 'v111'
  assert cd['k1/k11/k112/k1121'] == 'v1121'
  assert cd['k1/k11/k113'] == 'v113'

  assert cd['k1/k12/k111'] == 'v111f'
  assert cd['k1/k11/k112/k1122'] == 'v1122f'
  assert cd['k1/k12'].to_dict() == {
    'k111': 'v111f',
    'k112': {
      'k1121': 'v1121f',
      'k1122': 'v1122f',
    },
    'k113': 'v113f',
  }


def test_fallback_set():
  cd = ConfDict(
    k1={
      'k11': 'v11',
      'k12': 'v12',
    },
  )

  cd['fallback'] = {
    'k13': 'v13f',
  }

  assert cd['k1/k13'] == 'v13f'

  cd['fallback/k13'] = 'v13f_2'
  assert cd['k1/k13'] == 'v13f_2'


def test_fallback_delete():
  cd = ConfDict(
    fallback={
      'k13': 'v13f',
    },
    k1={
      'k11': 'v11',
      'k12': 'v12',
    },
  )

  del cd['fallback']
  with pytest.raises(KeyError):
    cd['k1/k13']


def test_fallback_update():
  cd = ConfDict(
    fallback={
      'k13': 'v13f',
    },
    k1={
      'k11': 'v11',
      'k12': 'v12',
    },
  )

  cd.update({
    'fallback': {
      'k13': 'v13f_2',
      'k14': 'v14f'
    },
  })
  assert cd['k1/k13'] == 'v13f_2'
  assert cd['k1/k14'] == 'v14f'


def test_fallback_contains():
  cd = ConfDict(
    fallback={
      'k13': 'v13f',
    },
    k1={
      'k11': 'v11',
      'k12': 'v12',
    },
  )
  # fallbacks are not contained
  assert not 'k1/k13' in cd


def test_fallback_interpolation():
  cd = ConfDict(
    k1={
      'fallback': {
        'k111': '{{<key>}}',
        'k112': '{{k111}}',
        'k113': '{{k112}}random{{k111}}',
      },
      'k11': {
        'k111': 'v111',
      },
    },
  )
  assert cd['k1/k12/k111'] == 'k12'
  assert cd['k1/k12/k112'] == 'k12'
  assert cd['k1/k12/k113'] == 'k12randomk12'
  assert cd['k1/k11/k112'] == 'v111'
  assert cd['k1/k11/k113'] == 'v111randomv111'
  assert cd['k1/fallback/k112'] == '{{k111}}'


def test_to_dict():
  cd = ConfDict(
    fallback={
      'k11': {
        'k111': 'v111f',
      },
      'k12': {
        'k121': '{{../k11/k111}}',
        'k122': '{{k121}}',
      },
    },
    k1={
      'k11': {
        'k111': 'v111',
        'k112': '{{k111}}',
      },
    },
  )

  assert cd.to_dict() == {
    'fallback': {
      'k11': {
        'k111': 'v111f',
      },
      'k12': {
        'k121': '{{../k11/k111}}',
        'k122': '{{k121}}',
      },
    },
    'k1': {
      'k11': {
        'k111': 'v111',
        'k112': 'v111',
      },
    },
  }


def test_custom_settings():
  test_config = {
    '__separator': '>',
    '__self_key': '!',
    '__parent_key': '!!',
    '__root_key': '!!!',
    '__key_key': '__key__',
    '__interpolation_regex': r'(\[\[([^\[\]]*)\]\])',
    '__fallback_key': 'fb',
  }

  cd = ConfDict(
    fb={
      'k11': {
        'k111': 'v111f',
      },
      'k12': {
        'k121': '[[!!>k11>k111]]',
        'k122': '[[k121]]',
      },
    },
    k1={
      'k11': {
        'k111': 'v111',
        'k112': '[[k111]]',
      },
    },
    **test_config,
  )

  assert cd['k1>k11>k111'] == 'v111'
  assert cd['!'] == cd
  assert cd['k1>k11>k112'] == 'v111'
  assert cd['k2>k12>k122'] == 'v111f'


def test_keys():
  cd = ConfDict(
    k1='v1',
    k2={
      'k21': 'v21',
      'k22': {
        'k221': 'v221',
      },
    },
    k3={
      'k31': 'v31',
      'k32': 'v32',
    },
  )

  assert list(cd.keys()) == [
    'k1',
    'k2/k21',
    'k2/k22/k221',
    'k3/k31',
    'k3/k32',
  ]


def test_items():
  cd = ConfDict(
    k1='v1',
    k2={
      'k21': 'v21',
      'k22': {
        'k221': 'v221',
      },
    },
    k3={
      'k31': 'v31',
      'k32': 'v32',
    },
  )

  assert list(cd.items()) == [
    ('k1', 'v1'),
    ('k2/k21', 'v21'),
    ('k2/k22/k221', 'v221'),
    ('k3/k31', 'v31'),
    ('k3/k32', 'v32'),
  ]


def test_to_str():
  cd = ConfDict(
    fallback={
      'k11': {
        'k111': 'v111f',
      },
      'k12': {
        'k121': '{{../k11/k111}}',
        'k122': '{{k121}}',
      },
    },
    k1={
      'k11': {
        'k111': 'v111',
        'k112': '{{k111}}',
      },
    },
  )

  assert str(cd) == dedent(
    '''
    ConfDict
    { 'fallback': { 'k11': {'k111': 'v111f'},
                    'k12': {'k121': '{{../k11/k111}}', 'k122': '{{k121}}'}},
      'k1': {'k11': {'k111': 'v111', 'k112': '{{k111}}'}}}
  '''
  )[1:-1]  # remove first and last newline


def test_realize():
  cd = ConfDict(
    fallback={
      'k11': {
        'k111': 'v111f',
        'k112': '{{../<key>}}',
      },
      'k12': {
        'k121': '{{../k11/k111}}',
        'k122': '{{k121}}',
      },
    },
    k2={
      'k23': 'v23',
    },
  )

  assert cd['k1'].to_dict() == {
    'k11': {
      'k111': 'v111f',
      'k112': 'k1',
    },
    'k12': {
      'k121': 'v111f',
      'k122': 'v111f',
    },
  }

  cd['k1'].realizeTo('.')
  cd['k2/k11'].realizeTo('k2')
  cd['k2/k12'].realizeTo('k2')

  del cd['fallback']

  assert cd['k1'].to_dict() == {
    'k11': {
      'k111': 'v111f',
      'k112': 'k1',
    },
    'k12': {
      'k121': 'v111f',
      'k122': 'v111f',
    },
  }

  assert cd['k2'].to_dict() == {
    'k11': {
      'k111': 'v111f',
      'k112': 'k2',
    },
    'k12': {
      'k121': 'v111f',
      'k122': 'v111f',
    },
    'k23': 'v23',
  }
