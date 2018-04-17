# nix

Built from [generator-python-lib](https://gitlab.com/hyper-expanse/generator-python-lib#readme)

[![codecov.io](https://codecov.io/gitlab/hbetts/orbitalpy/coverage.svg?branch=master)](https://codecov.io/gitlab/./nix?branch=master)

Smart data parser, can handle most fucked up data you can throw at it

## Installation
Test:

`python setup.py test`

Build:
`python3 setup.py build`

Install:
`python3 setup.py install`

## Usage

```
from nix.utils import Parser

>>> Parser([], '[1,2,3]')
[1, 2, 3]
```

## Development

```
virtualenv --python=python3 venv
source ./venv/bin/activate
python setup.py easy_install
pip install -r requirements-dev.txt
```



## Contributing

Read [CONTRIBUTING](CONTRIBUTING.md).
