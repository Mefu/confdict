# standard libs

# third party libs

# project imports
from confdict import ConfDict

def test_confdict():
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

  assert cd['k2/k22/../k21'] == cd['k2/k21']


  # interpolation
  assert cd['k5/k51'] == 'v32'
  assert cd['k5/k52/k521'] == 'v53'
  assert cd['k5/k52/k522'] == 'v53'

  # fallback
  # assert cd['k6/k61/k611'] == 'v611'
  # assert cd['k6/k61/k612/k6121'] == 'v6121'
  # assert cd['k6/k61/k612/k6122'] == 'v6122f'

  # update
  cd.update({
    'k2': {
      'k21': 'v21_2',
      'k22': {
        'k223': 'v223',
      },
    },
    'k5': {
      'k53': 'v53_2',
    },
    'k6': {
      'fallback': {
        'k612': {
          'k6122': 'v6122f_2',
        },
      },
    },
  })

  assert cd['k2/k21'] == 'v21_2'
  assert cd['k2/k22/k221'] == 'v221'
  assert cd['k2/k22/k222'] == 'v222'
  assert cd['k2/k22/k223'] == 'v223'
  assert cd['k5/k53'] == 'v53_2'

  # interpolation update
  assert cd['k5/k51'] == 'v32'
  assert cd['k5/k52/k521'] == 'v53_2'
  assert cd['k5/k52/k522'] == 'v53_2'

  # fallback update
  # assert cd['k6/k61/k612/k6122'] == 'v6122f_2'
