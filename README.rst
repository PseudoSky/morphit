MorPhit
===

Do you have "My data is fucked"
If you find yourself saying any of the following, you may to be entitled to financial compensation.

- WTF half of these are strings instead of **insert type here**
- How do I even convert from **insert type A** to **insert type B**
- I have so much bad data I'm going to have to manually fix
- I have hundreds of if conditions to fix weird data
- How the hell am I supposed to fix the type of all these nested objects
- You're telling me this float is supposed to be a date?...
- You're telling me that I cant put a datetime object anywhere?
- I don't know how any of these strings became numbers but...

morphit is a smart parser that takes a template for data and converts whatever you feed it into whatever you want it to be.

Features
------------

- datetime serialization

::
	Parser(str, datetime(2018, 1, 31, 6, 17, 45, 547000))
	>>> "2018-01-31T06:17:45.547"

- deep serialization of dicts
- supports custom serializers using methods/lambda functions
- templated parsers
- nested templated parsers



Supported Conversions
------------

- any -> list
- any -> object
- any -> tuple
- any -> type
- any -> str

- dict -> str[json]
- dict -> dict
- dict -> list
- dict -> tuple

- datetime -> str
- datetime -> str[json]
- datetime -> int
- datetime -> float
- datetime.time -> str
- datetime.date -> str

- float -> str
- float -> float
- float -> list
- float -> tuple
- float -> type
- float -> datetime

- int -> str
- int -> int
- int -> list
- int -> tuple
- int -> datetime
- int -> type

- list -> str[json]
- list -> list
- list -> tuple

- tuple -> str[json[list]]
- tuple -> list
- tuple -> tuple

- none -> str
- none -> bool
- none -> list
- none -> tuple

- str -> bool
- str -> datetime
- str -> dict
- str -> float
- str -> int
- str -> list
- str -> tuple
- str -> type
- str[iso8601] -> datetime
- str[iso8601] -> float
- str[unicode] -> any string conversions
- str[python] -> any string conversions


**iso8601** a date string formatted to the iso8601 spec
**json** a json encoded equivilent of the data
**unicode** strings that get messed up with u' ex: `"[u'this',u'that']"`
**python** strings that are weirdly single quoted ex: `"['photo', 2, 'pic', 'pics']"`

Installation
------------

Test:

``python setup.py test``

Build: ``python3 setup.py build``

Install: ``python3 setup.py install``

Usage
-----

::

   from nix.utils import Parser

   >>> Parser([], '[1,2,3]')
   [1, 2, 3]

Development
-----------

::

   virtualenv --python=python3 venv
   source ./venv/bin/activate
   python setup.py easy_install
   pip install -r requirements-dev.txt


Roadmap
------------

- Add strict parameter that enables enforcement of keys and list/tuple length
- Add default parameter that remplaces None or non existing values with a specified default
- Add custom parser type that accepts a lambda function that is applied to the value
- Add fallback parameter that accepts a value or a lambda function to replace the value

Contributing
------------

Read `CONTRIBUTING`_.

Make a PR and I'll give it a look

Odds are good / the goods are odd
