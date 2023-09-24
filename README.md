# MorPhit

Usage
------------

```python
    >>> from morphit import Parser
    >>> Parser([], '[1,2,3]')
    [1, 2, 3]
```

`pip install morphit`

`sudo -H pip install morphit`


morphit is a no nonsense parser that takes any input and converts it to the correct type based on a provided template
IE: Parse bad data from whatever you feed in - into whatever you want it to be

Example developer experiences
-   Half of these values are **_strings_** instead of ______ **_correct_type_** _____
-   How do I convert from ___ **_incorrect_type_** ___ to ______ **_correct_type_** _____
-   I have so much bad data I'm going to have to manually fix
-   I have hundreds of if conditions to fix weird data
-   How can I fix types within a set of deeply nested objects?
-   This float is supposed to be a date?...
-   You're telling me that I can't persist an object with a property of type datetime?


Features
------------

-   Processor chaining

```python
>>> from morphit import Processor

>>> Processor.flow(["<parser|lambda|func|obj>",...])

>>> p = Processor(dict)
>>> p.then(lambda d: d['date'])
     .then(Processor.types['Date'])
>>> res = p('{"date": "2018-01-31T06:17:45.547"}')

datetime(2018, 1, 31, 6, 17, 45, 547000)
```

-   datetime serialization

```python
>>> from datetime import date
>>> Parser(str, datetime(2018, 1, 31, 6, 17, 45, 547000))
"2018-01-31T06:17:45.547"
```

-   deep serialization of dicts
-   supports custom serializers using methods/lambda functions
-   templated parsers
-   nested templated parsers

Supported Conversions
------------

-   any -> list
-   any -> object
-   any -> tuple
-   any -> type
-   any -> str
-   dict -> str[json]
-   dict -> dict
-   dict -> list
-   dict -> tuple
-   datetime -> str
-   datetime -> str[json]
-   datetime -> int
-   datetime -> float
-   datetime.time -> str
-   datetime.date -> str
-   float -> str
-   float -> float
-   float -> list
-   float -> tuple
-   float -> type
-   float -> datetime
-   int -> str
-   int -> int
-   int -> list
-   int -> tuple
-   int -> datetime
-   int -> type
-   list -> str[json]
-   list -> list
-   list -> tuple
-   tuple -> str[json[list]]
-   tuple -> list
-   tuple -> tuple
-   none -> str
-   none -> bool
-   none -> list
-   none -> tuple
-   str -> bool
-   str -> datetime
-   str -> dict
-   str -> list
-   str -> tuple
-   str[int] -> float
-   str[int] -> int
-   str[float] -> float
-   str[float] -> int
-   str -> type
-   str[iso8601] -> datetime
-   str[iso8601] -> float
-   str[unicode] -> any string conversions
-   str[python] -> any string conversions

**iso8601** a date string formatted to the iso8601 spec
**json** a json encoded equivilent of the data
**unicode** strings that get messed up with u' ex: "[u'this',u'that']"
**python** strings that are weirdly single quoted ex: "['photo', 2, 'pic', 'pics']"

Installation
------------

`pip3 install morphit`

`sudo -H pip3 install morphit`

Deploy
------------

```sh
python3 setup.py build             #Build:
python setup.py coverage           #Test
python3 setup.py install           #Install:
rm -rf build morphit.egg-info dist #Cleanup
```

Deploy
------------

* Run tests as outlined above
* Make sure you bump the version
* Check venv is active


```sh
echo "__version__=1.x.y" > ./morphit/version.py # where x and y are the next version
python3 setup.py coverage
python3 setup.py sdist bdist_wheel
twine upload dist/*
```

Development
------------
```sh
virtualenv --python=python3 venv
source ./venv/bin/activate
python setup.py easy_install
pip install -r requirements-dev.txt
```

Roadmap
------------

- Custom exceptions for bad casting (int/list/tuple -> dict)
- Add strict parameter that enables enforcement of keys and list/tuple length
- Add default parameter that remplaces None or non existing values with a specified default
- Add fallback parameter that accepts a value or a lambda function to replace the value


CHANGELOG
------------
## 1.2.0
Added custom aggregators for processors to allow result merging without needing to update the chained partial object.
- FIX: Coverage was broken due to the import of version in setup.py
- FEATURE: Custom aggregators for Processor class

## 1.1.0
Breaking changes: removed `Template` class, types are now attached to `Processor`

- FIX: 100% test coverage, all dead code eliminated
- FIX: primitive to iterable casting
- FEATURE: Removed & Replaced `Template` with `Processor` callable class
- FEATURE: Added processor chaining `then` `flow`
- FEATURE: Added lambda Processor original data & result parameters


BUGS
-----------



Contributing
------------

Read CONTRIBUTING\_.

Make a PR and I'll give it a look

Odds are good / the goods are odd
