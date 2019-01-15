# standard libs

# third party libs
import pytest

# project imports
from confdict import ConfDict

def test_confdict(capsys):
  with capsys.disabled():
    cd = ConfDict(
      k1 = 'v1',
      k2 = {
        'k21': 'v21',
        'k22': {
          'k221': 'v221',
          'k222': 'v222',
        }
      },
      k3 = {
        'k31': 'v31',
        'k32': 'v32',
      },
      k5 = {
        'k51': '{{.../k3/k32}}',
        'k52': {
          'k521': '{{./k522}}',
          'k522': '{{../k53}}',
          'k523': '{{<key>}}',
        },
        'k53': 'v53',
      },
      k6 = {
        'fallback': {
          'k611': 'v611f',
          'k612': {
            'k6121': 'v6121f',
            'k6122': 'v6122f',
          },
          'k613': '{{<key>}}',
        },
        'k61': {
          'k611': 'v611',
          'k612': {
            'k6121': 'v6121',
          },
        },
      },
    )

    # standard access
    assert cd['k1'] == 'v1'
    assert cd['k2/k22/k222'] == 'v222'
    assert cd['k2']['k22/k222'] == 'v222'
    assert cd['k2']['k22']['k222'] == 'v222'
    assert cd['k3'] == { 'k31': 'v31', 'k32': 'v32', }

    # relative access
    assert cd['.'] == cd
    assert cd['k2/..'] == cd
    assert cd['k2/k22/...'] == cd
    assert cd['k2/k22/../k21'] == cd['k2/k21']


    # interpolation
    assert cd['k5/k51'] == 'v32'
    assert cd['k5/k52/k521'] == 'v53'
    assert cd['k5/k52/k522'] == 'v53'
    assert cd['k5/k52/k523'] == 'k52'

    # fallback
    assert cd['k6/k61/k611'] == 'v611'
    assert cd['k6/k61/k612/k6121'] == 'v6121'
    assert cd['k6/k61/k612/k6122'] == 'v6122f'

    # fallback and interpolation
    assert cd['k6/k62/k613'] == 'k62'

    # update
    cd.update({
      'k2': {
        'k21': 'v21_2',
        'k22': {
          'k223': 'v223',
        },
      },
      'k5': {
        'fallback': {
          'k541': 'v541f',
          'k542': {
            'k5421': 'v5421f',
          },
        },
        'k53': 'v53_2',
      },
      'k6': {
        'fallback': {
          'k612': {
            'k6122': 'v6122f_2',
          },
        },
      },
      'k7': {
        'k71': 'v71',
        'k72': {
          'k721': 'v721',
          'k722': 'v722',
        },
      },
    })

    assert cd['k2/k21'] == 'v21_2'
    assert cd['k2/k22/k221'] == 'v221'
    assert cd['k2/k22/k222'] == 'v222'
    assert cd['k2/k22/k223'] == 'v223'
    assert cd['k5/k53'] == 'v53_2'
    assert cd['k7/k72/k721'] == 'v721'

    # interpolation update
    assert cd['k5/k51'] == 'v32'
    assert cd['k5/k52/k521'] == 'v53_2'
    assert cd['k5/k52/k522'] == 'v53_2'

    # fallback update
    assert cd['k5/k54/k541'] == 'v541f'
    assert cd['k5/k54/k542'] == { 'k5421': 'v5421f' }
    assert cd['k6/k61/k612/k6122'] == 'v6122f_2'

    # cannot update

    # delete
    del cd['k2/k22/k222']
    del cd['k6/k61/k612/k6121']
    del cd['k5/k53']
    del cd['k6/fallback/k611']
    del cd['k7/k72']

    with pytest.raises(KeyError):
      cd['k2/k22/k222']

    with pytest.raises(KeyError):
      cd['k7/k72']

    # interpolation fallback
    with pytest.raises(KeyError):
      cd['k5/k52/k521']

    with pytest.raises(KeyError):
      cd['k5/k52/k522']

    # delete fallback
    assert cd['k6/k61/k612/k6121'] == 'v6121f'


    # to dict
    cd['k5/k53'] = 'v53_3'

    assert cd.to_dict() == {
      'k1': 'v1',
      'k2': {
        'k21': 'v21_2',
        'k22': {
          'k221': 'v221',
          'k223': 'v223',
        },
      },
      'k3': {
        'k31': 'v31',
        'k32': 'v32',
      },
      'k5': {
        'fallback': {
          'k541': 'v541f',
          'k542': {
            'k5421': 'v5421f',
          },
        },
        'k51': 'v32',
        'k52': {
          'k521': 'v53_3',
          'k522': 'v53_3',
          'k523': 'k52',
        },
        'k53': 'v53_3',
      },
      'k6': {
        'fallback': {
          'k612': {
            'k6121': 'v6121f',
            'k6122': 'v6122f_2',
          },
          'k613': '{{<key>}}',
        },
        'k61': {
          'k611': 'v611',
          'k612': {
          },
        },
      },
      'k7': {
        'k71': 'v71',
      },
    }

    # str
    assert str(cd)[:8] == 'ConfDict'
