"""
General purpose utility library..
"""

import re, string
import iso8601
from datetime import datetime, date, time
from multipledispatch import dispatch
import json

class JSONEncoder(json.JSONEncoder):
    """JSONEncoder subclass that knows how to encode date/time, decimal types, and UUIDs."""

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            if o.utcoffset() is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        else:
            return super(JSONEncoder, self).default(o)


pattern = re.compile('[\W_]+')

DateType = datetime.now()

class StaticDateType():
  def __init__(self):
    pass

# OUTPUT: fallback to the type of input
@dispatch(object, object)
def Parser(base, var):
  if(base is None):
    return var
  if(var is None):
    var=0
  if type(base) == type(var):
    return var
  return type(base)(var)

# TODO: THIS IS BAD
@dispatch((type(DateType), StaticDateType), str)
def Parser(base, var):
  tmp=var.split('.')
  if(var.isdigit() or (len(tmp)==2 and tmp[0].isdigit() and tmp[1].isdigit())):
    return Parser(base, float(var))
  return iso8601.parse_date(var)

@dispatch((type(DateType), StaticDateType), (int, float))
def Parser(base, var):
  if(var > 150000000000): # Check if ms timestamp
    return datetime.fromtimestamp(var / 1e3)
  return datetime.fromtimestamp(var)

@dispatch((list, tuple), (float, int, str))
def Parser(base, var):
  return type(base)([var])

@dispatch(type(str), (object))
def Parser(base, var):
  return Parser(base(), var)
  # if("%s"%base=="<class 'type'>" or "%s"%base=="<class 'bool'>" or "%s"%base=="<class 'str'>"):
  # else:
  #   return base(var)

# OUTPUT: json
@dispatch((str), (dict, list, tuple))
def Parser(base, var):
  return json.dumps(var, cls=JSONEncoder)

# OUTPUT: list or tuple
@dispatch((list, tuple), (list, tuple, object))
def Parser(base, var):
  if(len(base)>0):
    return type(base)([Parser(base[0], e) for e in var])
  return type(base)([e for e in var])

# OUTPUT: list
@dispatch(list, str)
def Parser(base, var):
  if("u'" in var or not '"' in var):
    var = var.replace("u'", '"').replace("'", '"')
  if(len(base)>0):
    return [Parser(base[0], var_elem) for var_elem in json.loads(var)]
  return json.loads(var)

# OUTPUT: boolean
@dispatch(bool, str)
def Parser(base, var):
  return var =='True'

# OUTPUT: number
@dispatch((float, int), str)
def Parser(base, var):
  var = var.replace(' ','')
  try:

    if(var is None): raise Exception('uhh')
    if(var == ''): var = '-1'
    var = var.replace(' ','').replace(',','')
    if(var.count('.')>1):var = var.replace('.','')
    return type(base)(var)
  except Exception as e:
    # print(e)
    print(base, var, type(base))
    raise e
  else:
    pass

# OUTPUT: dict recursively
@dispatch(dict, dict)
def Parser(base, var):
  for k in base.keys():
    if(k in var):
      if(var[k]=='N/A'):var[k]=0.0
      if(base[k]=='N/A'):base[k]=0.0
      # print(type(base[k]), base[k])
      var[k] = Parser(base[k], var[k])
  return var

# OUTPUT: dict from json
@dispatch(dict, str)
def Parser(base, var):
  temp = json.loads(var.replace("u'", '"').replace("'", '"'))
  return Parser(base, temp)


class ParserTemplate():
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

  # @classmethod
  def run(self, data):
      return Parser(self.template, data)