"""
General purpose utility library..
"""

import re, string, json, iso8601
from types import LambdaType, FunctionType
from datetime import datetime, date, time, timezone
import time as pytime
from multipledispatch import dispatch

def getLast(results): return results[-1]
def getRest(results): return results[1:]
def getMergedDicts(results): return dict(i for r in results[1:] for i in r.items())

Aggregators = {
  'map': getRest,
  'reduce': getLast,
  'merge': getMergedDicts,
}

Instances = {
  'datetime': datetime(2019, 12, 6, 20, 31, 59, 329921),
  'time': time(6,17, 45, 547000),
  'date': date(2018, 1, 31),
  'none': None,
  'lambda': lambda x: x,
  'function': print,
}

Types = {
  'date':     type(Instances['date']),
  'datetime': type(Instances['datetime']),
  'time':     type(Instances['time']),
  'none':     type(None),
  'lambda':   LambdaType,
  'function': FunctionType,
}

class JSONEncoder(json.JSONEncoder):
    """JSONEncoder subclass that knows how to encode date/time, decimal types, and UUIDs."""

    # This function is called when the base serializer doesn't know wtd with type
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if (type(o) in [datetime, time, date]):
          return Parser(str, o)
        elif(callable(o) and o.__code__.co_argcount==0):
          return o()
        else:
          return None


# Returns a function that parses to a given type (base)
class Processor():
  def __init__(self, startBase, aggregator='reduce'):
    # aggregator=='merge' requires an object to be resolved
    if(aggregator in Aggregators):
      self.aggregator = Aggregators[aggregator]
    else:
      self.aggregator = Processor(aggregator)
    self.templates = []
    self.then(startBase)



  def __call__(self, var, fallback=None, output_default={}):
    # Allow the original fallback in a pipe to be passed to parser
    # Used for chained functions with reference to original values
    curry = var if fallback is None else fallback
    results = [var]
    for base in self.templates:
      results.append(Parser(base, results[-1], curry))
    output = self.aggregator(results)
    return output


  @property
  def __code__(self):
    return self.__call__.__code__

  @staticmethod
  def flow(templates, aggregator='reduce'):
    r = Processor(templates[0], aggregator=aggregator)
    if(len(templates)==1): return r
    for p in templates[1:]:
      r.then(Processor(p))
    return r

  def then(self, base):
    self.templates.append(base)
    return self

# Wrapper for fallback defaulting
@dispatch(object, object)
def Parser(base, var):
  return Parser(base, var, None)

# OUTPUT: fallback to the type of input
@dispatch(object, object, object)
def Parser(base, var, fallback):
  if type(base) == type(var):
    return var
  if(base is None):
    return var
  if(var is None):
    return fallback() if callable(fallback) else fallback
  return type(base)(var)

# datetime -> timestamp
@dispatch(int, Types['datetime'], object)
def Parser(base, var, fallback):
  return int(var.timestamp()*1000)

# datetime -> float
@dispatch(float, Types['datetime'], object)
def Parser(base, var, fallback):
  return pytime.mktime(var.timetuple()) + var.microsecond / 1E6

# float -> datetime
@dispatch(Types['datetime'], float, object)
def Parser(base, var, fallback):
  return datetime.fromtimestamp(var)

# datetime.date -> str (iso format)
@dispatch(str, Types['date'], object)
def Parser(base, var, fallback):
  return var.isoformat()

# datetime -> str
@dispatch(str, Types['datetime'], object)
def Parser(base, var, fallback):
  r = var.isoformat()
  if var.microsecond:
      r = r[:23] + r[26:]
  if r.endswith('+00:00'):
      r = r[:-6] + 'Z'
  return r

# datetime.time -> string
@dispatch(str, Types['time'], object)
def Parser(base, var, fallback):
  # TODO: test error
  if var.utcoffset() is not None:
      raise ValueError("JSON can't represent timezone-aware times.")

  r = var.isoformat()
  if var.microsecond:
      r = r[:12]
  return r

# any -> func(any)
@dispatch((Types['function'], Types['lambda']), object, object)
def Parser(base, var, fallback):
  if(base.__code__.co_argcount==1):
    return base(var)
  return base(var, fallback)

# any -> func(any)
@dispatch(Processor, object, object)
def Parser(base, var, fallback):
  return base(var, fallback)

@dispatch(Types['datetime'], str, object)
def Parser(base, var, fallback):
  tmp=var.split('.')
  if(len(tmp)==2 and tmp[0].isdigit() and tmp[1].isdigit()):
    return Parser(base, float(var), fallback)
  elif(var.isdigit()):
    return Parser(base, int(var), fallback)
  return iso8601.parse_date(var)

# str -> datetime.date
@dispatch(Types['date'], str, object)
def Parser(base, var, fallback):
  return Parser(Instances['datetime'], var, fallback).date()

# int,float -> datetime.date
@dispatch(Types['date'], (int, float), object)
def Parser(base, var, fallback):
  if(var > 150000000000): # Check if ms timestamp
    return datetime.fromtimestamp(var / 1e3)
  return datetime.fromtimestamp(var)

# any -> type(any)
@dispatch(type(str), (object), object)
def Parser(base, var, fallback):
  return Parser(base(), var, fallback)

# OUTPUT: json
# dict, array -> str(json)
@dispatch((str), (dict, list, tuple), object)
def Parser(base, var, fallback):
  return json.dumps(var, cls=JSONEncoder)

# primitive -> array
@dispatch((list, tuple), (float, int, str), object)
def Parser(base, var, fallback):
  return Parser(base, [var], fallback)

# OUTPUT: list or tuple
# any -> array
@dispatch((list, tuple), (list, tuple, object), object)
def Parser(base, var, fallback):

    if(len(base)>1): # CASE: cast each
        res = []
        m = min(len(base),len(var))
        res = [Parser(base[i], var[i], fallback) for i in range(m)]
        res = res + list(var[m:])
        return type(base)(res)
    elif(len(base)==1): # CASE: single type casting
        return type(base)([Parser(base[0], e, fallback) for e in var])
    return type(base)([e for e in var])

# OUTPUT: list recursively parses json if well formatted
# str -> list
@dispatch(list, str, object)
def Parser(base, var, fallback):
  if("u'" in var or not '"' in var):
    var = var.replace("u'", '"').replace("'", '"')
  # Guess if str is well formatted
  if(var.startswith('[') and var.endswith(']')):
    tmp = json.loads(var)
  else:
    tmp = [var]
  if(len(base)>0):
    return [Parser(base[0], var_elem, fallback) for var_elem in tmp]
  return tmp

# OUTPUT: boolean
# str -> bool
@dispatch(bool, str, object)
def Parser(base, var, fallback):
  return var =='True' or var =='1' or var =='t' or var =='1.0'

# OUTPUT: string
# null -> str
@dispatch(str, Types['none'], object)
def Parser(base, var, fallback):
  return 'None'

# OUTPUT: boolean
# null -> float
@dispatch((float, int), Types['none'], object)
def Parser(base, var, fallback):
  return type(base)(0)

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
@dispatch((float, int), str, object)
def Parser(base, var, fallback):
  var = var.replace(' ','')
  try:
    if(var == ''): var = '0'
    var = re.sub('[^0-9.-]', '', var) # Adds support for currency
    if(var.count('.')>1):var = var.replace('.','')
    return type(base)(float(var))
  except Exception as e:
    raise ValueError("Unable to cast %s -> %s"%(var, type(base)))

# OUTPUT: dict recursively. AKA: nested type formatting
# dict -> dict
@dispatch(dict, dict, object)
def Parser(base, var, fallback):
  for k in base.keys():
    if(k in var):
      if(var[k]=='N/A'):var[k]=0.0
      if(base[k]=='N/A'):base[k]=0.0
      var[k] = Parser(base[k], var[k], fallback)
  return var

# OUTPUT: dict from json string
# str -> dict
@dispatch(dict, str, object)
def Parser(base, var, fallback):
  temp = json.loads(var.replace("u'", '"').replace("'", '"'))
  return Parser(base, temp, fallback)
