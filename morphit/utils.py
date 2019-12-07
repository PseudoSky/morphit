"""
General purpose utility library..
"""

import re, string, json, iso8601
from types import LambdaType, FunctionType
from datetime import datetime, date, time
import time as pytime
from multipledispatch import dispatch


class JSONEncoder(json.JSONEncoder):
    """JSONEncoder subclass that knows how to encode date/time, decimal types, and UUIDs."""

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if (type(o) in [datetime, time, date]):
          return Parser(str, o)
        return super(JSONEncoder, self).default(o)

pattern = re.compile('[\W_]+')
DateType = datetime.now()
NoneType = type(None)

class StaticDateType(object):
  def __init__(self):
    pass

class Template(object):
  types = {
    'Date': DateType,
    'StaticDateType': StaticDateType,
  }

  def __init__(self, template=None, strict=False):
    self.template = template
    self.strict = strict

  @staticmethod
  def parse(template, data):
    return Parser(template, data)

  def run(self, data):
    return Parser(self.template, data)

# Returns a function that parses to a given type (base)
def Processor(base):
  return lambda var: Parser(base, var)

# OUTPUT: fallback to the type of input
@dispatch(object, object)
def Parser(base, var, fallback=None):
  if(base is None):
    return var
  if(var is None):
    var=0
  if type(base) == type(var):
    return var
  if (not fallback is None):
    return Parser(fallback, var)
  return type(base)(var)

# datetime -> str
@dispatch(str, datetime)
def Parser(base, var, fallback=None):
  r = var.isoformat()
  if var.microsecond:
      r = r[:23] + r[26:]
  if r.endswith('+00:00'):
      r = r[:-6] + 'Z'
  return r

# datetime -> timestamp
@dispatch(int, datetime)
def Parser(base, var, fallback=None):
  return int(var.timestamp()*1000)

# datetime -> float
@dispatch(float, datetime)
def Parser(base, var, fallback=None):
  return pytime.mktime(var.timetuple()) + var.microsecond / 1E6

# float -> datetime
@dispatch(datetime, float)
def Parser(base, var, fallback=None):
  return datetime.fromtimestamp(var)

# datetime.date -> str (iso format)
@dispatch(str, date)
def Parser(base, var, fallback=None):
  return var.isoformat()

# datetime.time -> string
@dispatch(str, time)
def Parser(base, var, fallback=None):
  if var.utcoffset() is not None:
      raise ValueError("JSON can't represent timezone-aware times.")
  r = var.isoformat()
  if var.microsecond:
      r = r[:12]
  return r

# any -> Template
@dispatch(Template, object)
def Parser(base, var, fallback=None):
  return base.run(var)

# any -> func(any)
@dispatch((FunctionType, LambdaType), object)
def Parser(base, var, fallback=None):
  return base(var)

# TODO: THIS IS BAD

# str -> iso8601
@dispatch((type(DateType), StaticDateType), str)
def Parser(base, var, fallback=None):
  tmp=var.split('.')
  if(var.isdigit() or (len(tmp)==2 and tmp[0].isdigit() and tmp[1].isdigit())):
    return Parser(base, float(var))
  return iso8601.parse_date(var)

# str -> datetime.date
@dispatch(datetime, str)
def Parser(base, var, fallback=None):
  tmp=var.split('.')
  if('-' in var):
    return iso8601.parse_date(var)
  elif(len(tmp)==2 and tmp[0].isdigit() and tmp[1].isdigit()):
    return Parser(base, float(var))
  elif(var.isdigit()):
    return Parser(base, int(var))
  return iso8601.parse_date(var)

# int,float -> datetime.date
@dispatch((type(DateType), StaticDateType), (int, float))
def Parser(base, var, fallback=None):
  if(var > 150000000000): # Check if ms timestamp
    return datetime.fromtimestamp(var / 1e3)
  return datetime.fromtimestamp(var)

# primitive -> array
@dispatch((list, tuple), (float, int, str))
def Parser(base, var, fallback=None):
  return type(base)([var])

# any -> type(any)
@dispatch(type(str), (object))
def Parser(base, var, fallback=None):
  return Parser(base(), var)

# OUTPUT: json
# dict, array -> str(json)
@dispatch((str), (dict, list, tuple))
def Parser(base, var, fallback=None):
  return json.dumps(var, cls=JSONEncoder)

# OUTPUT: list or tuple
# any -> array
@dispatch((list, tuple), (list, tuple, object))
def Parser(base, var, fallback=None):
    if(len(base)>1): # CASE: cast each
        res = []
        m = min(len(base),len(var))
        res = [Parser(base[i], var[i]) for i in range(m)]
        res = res + list(var[m:])
        return type(base)(res)
    elif(len(base)==1): # CASE: single type casting
        return type(base)([Parser(base[0], e) for e in var])
    return type(base)([e for e in var])

# OUTPUT: list recursively parses json if well formatted
# str -> list
@dispatch(list, str)
def Parser(base, var, fallback=None):
  if("u'" in var or not '"' in var):
    var = var.replace("u'", '"').replace("'", '"')
  # Guess if str is well formatted
  if(var.startswith('[') and var.endswith(']')):
    tmp = json.loads(var)
  else:
    tmp = [var]
  if(len(base)>0):
    return [Parser(base[0], var_elem) for var_elem in tmp]
  return tmp

# OUTPUT: boolean
# str -> bool
@dispatch(bool, str)
def Parser(base, var, fallback=None):
  return var =='True' or var =='1' or var =='t' or var =='1.0'

# OUTPUT: string
# null -> str
@dispatch(str, NoneType)
def Parser(base, var, fallback=None):
  return 'None'

# OUTPUT: boolean
# null -> float
@dispatch((float, int), NoneType)
def Parser(base, var, fallback=None):
  return type(base)(0)

#
'''
OUTPUT: number
NOTE: type(base)(float(var))
PURPOSE: Protect against the case below

>>> Parser(60, '150.0') # fails on type(base)(var) == int(var)

>>> int('150.0')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ValueError: invalid literal for int() with base 10: '150.0'
'''
# str -> float
@dispatch((float, int), str)
def Parser(base, var, fallback=None):
  var = var.replace(' ','')
  try:
    if(var == ''): var = '0'
    var = re.sub('[^0-9.-]', '', var) # Adds support for currency
    if(var.count('.')>1):var = var.replace('.','')
    return type(base)(float(var))
  except Exception as e:
    print(base, var, type(base))
    raise e

# OUTPUT: dict recursively. AKA: nested type formatting
# dict -> dict
@dispatch(dict, dict)
def Parser(base, var, fallback=None):
  for k in base.keys():
    if(k in var):
      if(var[k]=='N/A'):var[k]=0.0
      if(base[k]=='N/A'):base[k]=0.0
      var[k] = Parser(base[k], var[k])
  return var

# OUTPUT: dict from json string
# str -> dict
@dispatch(dict, str)
def Parser(base, var, fallback=None):
  temp = json.loads(var.replace("u'", '"').replace("'", '"'))
  return Parser(base, temp)
