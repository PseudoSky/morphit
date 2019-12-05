"""
morphit tests.
"""

import unittest
from morphit import Parser, Template
from datetime import datetime, timezone

class TestUtils(unittest.TestCase):
    """
    Test morphit's utils.
    """

    def setUp(self):
        self.template = {
            'dict':dict,
            'tojson':str,
            'tupletojson': (str,),
            'this':float,
            'other':2.0,
            'that': bool,
        }

    def test_case_float_string_to_int(self):
        res = Parser(60, '150.0')
        self.assertEqual(res, 150)
        res = Parser(90, '0.0')
        self.assertEqual(res, 0)
        res = Parser(90, '.0')
        self.assertEqual(res, 0)


    def test_simple_case_one(self):
        case = "[\"earthofficial\", \"blackandwhite\", \"worldshotz\"]"
        res = Parser([], case)
        self.assertEqual(res, ["earthofficial", "blackandwhite", "worldshotz"])

    def test_simple_case_two(self):
        case = "['photo', 'photos', 'pic', 'pics']"
        res = Parser([], case)
        self.assertEqual(res, ['photo', 'photos', 'pic', 'pics'])

    def test_simple_case_three(self):
        case = "['photo', 2, 'pic', 'pics']"
        res = Parser([], case)
        self.assertEqual(res, ['photo', 2, 'pic', 'pics'])

    def test_simple_case_four(self):
        case = "['photo', 2, 'pic', 'pics']"
        res = Parser(['strings'], case)
        self.assertEqual(res, ['photo', '2', 'pic', 'pics'])

    def test_parse_nested_objects(self):
        res = Parser(self.template, "{u'dict':{u'check':u'yup'}, u'tojson':{u'check':u'yup'}, 'tupletojson':[9,9], u'this':u'2.0','other': '2', 'that':'False'}")
        self.assertEqual(type(res),type({}))
        self.assertEqual(type(res['that']), type(False))
        self.assertEqual(res['that'], False)
        self.assertEqual({'check': 'yup'}, res['dict'])
        self.assertEqual('{\"check\": \"yup\"}', res['tojson'])
        self.assertEqual(('9', '9'), res['tupletojson'])


    def test_python_unicode_to_array(self):
      res = Parser([], "[u'this',u'that']")
      self.assertEqual(res, ['this','that'])

    def test_string_int_to_float(self):
      res = Parser(2.0, '3')
      self.assertEqual(res, 3.0)

    def test_string_int_to_typed_cast(self):
      res = Parser(float, '2')
      self.assertEqual(res, 2.0)

    def test_tuple_of_ints_to_list_of_floats(self):
      res = Parser([2.0], (9, 9))
      self.assertEqual( res, [9.0,9.0])

    def test_nested_list_type_cast(self):
      res = Parser(([9, 9],), [(2.0,9)])
      self.assertEqual(res, ([2,9],))

    def test_inconsistant_nested_types(self):
      res = Parser(([9.0, 9.0],), ([2.0,9],9))
      self.assertEqual( res, ([2.0,9.0],[9]) )

    def test_list_of_tuple_int_cast(self):
      res = Parser([(9,)], [(2.0, 9)])
      self.assertEqual(res , [(2,9)])

    def test_list_to_tuple_cast(self):
      res = Parser([(9,9)], ([2.0, 9],))
      self.assertEqual(res ,[(2,9)] )

    def test_float_to_str_cast(self):
      res = Parser('', 6.4)
      self.assertEqual(res , '6.4')

    def test_int_to_str_cast(self):
      res = Parser('', 6)
      self.assertEqual(res , '6')

    def test_bool_to_str_cast(self):
      res = Parser('', True)
      self.assertEqual(res , 'True')

    def test_none_to_str_cast(self):
      res = Parser('', None)
      self.assertEqual(res , 'None')

    def test_none_to_str_cast(self):
      res = Parser('', None)
      self.assertEqual(res , 'None')

    def test_currency_to_float_cast(self):
      res = Parser(1.0, '$10,000.00')
      self.assertEqual(res , 10000.00)

    def test_currency_to_int_cast(self):
      res = Parser(int, '$10,000.00')
      self.assertEqual(res , 10000)


    def test_none(self):
      pt = Template({
        'amount': 0.66075377,
        'datetime': Template.types['Date'],
        'fee': None,
        'id': None,
        'price': 10000.0,
        'info': ['659.100000', '0.66075377', 1517364874.3597, 's', 'l', ''],
      })

      tmp ={
        'amount': 0.66075377,
        'datetime': '2018-01-31T02:14:34.359Z',
        'fee': None,
        'id': None,
        'price': '$10,000.00',
        'info': ['659.100000', '0.66075377', 1517364874.3597, 's', 'l', ''],
      }
      self.assertEqual(pt.run(tmp), tmp)

    '''
    Test Date Parsing
    '''

    def test_string_float_ts(self):
      # Parse ms timestamp format (like from python)
      pt = Template(Template.types['Date'])
      tmp ='1517408042.277897'
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2, 277897), pt.run(tmp))
      tmp ='1517408042'
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2), pt.run(tmp))

    def test_s_ts(self):
      # Parse ms timestamp format (like from python)
      pt = Template(Template.types['Date'])
      tmp = 1517408042.277897
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2, 277897), pt.run(tmp))
      tmp = 1517408042
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2), pt.run(tmp))



    def test_string_ms_ts(self):
      # Parse s timestamp format (like from python)
      pt = Template(Template.types['Date'])
      tmp ='1517408265547'
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), pt.run(tmp))


    def test_ms_ts(self):
      # Parse s timestamp format (like from python)
      pt = Template(Template.types['Date'])
      tmp = 1517408265547
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), pt.run(tmp))

    def test_json_dump_datetime(self):
      # Test the json datetime encoder
      pt = Template(Template.types['Date'])
      tmp = pt.run(1517408265547)
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), tmp)
      res = Parser('', {'datetime': tmp})
      self.assertEqual('{"datetime": "2018-01-31T06:17:45.547"}', res)

    def test_datetime_to_str(self):
      # Test the json datetime encoder
      res = Parser(str, datetime(2018, 1, 31, 6, 17, 45, 547000))
      self.assertEqual("2018-01-31T06:17:45.547", res)

    def test_str_to_datetime(self):
      # Test the json datetime encoder
      res = Parser(datetime(2018, 1, 31, 6, 17, 45, 547000), "2018-01-31T06:17:45.547")
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000, tzinfo=timezone.utc), res)

    def test_datetime_to_int_cast(self):
      # Test the timestamp encoding a datetime to int
      pt = Template(int)
      tmp = pt.run(datetime(2018, 1, 31, 6, 17, 45, 547000))
      self.assertEqual(1517408265547, tmp)

    def test_datetime_to_float_cast(self):
      # Test encoding a datetime to a float
      pt = Template(float)
      tmp = pt.run(datetime(2018, 1, 31, 6, 14, 2, 277897))
      self.assertEqual(1517408042.277897, tmp)

    def test_datetime_to_str_cast(self):
      # Test encoding a datetime to a float
      pt = Template(str)
      tmp = pt.run(datetime(2018, 1, 31, 6, 17, 45, 547000))
      self.assertEqual("2018-01-31T06:17:45.547", tmp)

    def test_lambda_conversion(self):
      # Executes the lambda passed in rather than using builtin
      pt = Template(lambda x: int(x)*10)
      self.assertEqual(10, pt.run('1'))

    def test_function_conversion(self):
      # Executes the function passed in rather than using builtin
      def convert_multiply(var): return int(var)*10
      pt = Template(convert_multiply)
      self.assertEqual(10, pt.run('1'))

    '''
    Fancier nesting cases
    '''

    def test_flat_array(self):
      tmp = [659.100000, '0.66075377', 1517364874.3597, 's', 'l', '']
      test = ['659.100000', '', 1, 1]
      res = Parser(tmp, test)
      self.assertEqual(res, [659.100000, 0.0, 1.0, 1.0])

    def test_deep_array(self):
      tmp = [{ 'deep_bool': True, 'deep_float': 1.0 }]
      test = ["{ 'deep_bool': true, 'deep_float': \"1.0\" }"]
      res = Parser(tmp, test)
      self.assertEqual(res[0]['deep_bool'], True)
      self.assertEqual(res[0]['deep_float'], 1.0)
      self.assertEqual(len(res), 1)
      self.assertEqual(len(res[0].keys()), 2)

    def test_nested_parser_template(self):
      TickerModel = Template({
        'amount': 0.66075377,
        'datetime': Template.types['Date'],
        'fee': None,
        'id': None,
        'info': ['659.100000', '0.66075377', 1517364874.3597, 's', 'l', ''],
      })

      TickerListTemplate = Template({
        'tickers': [TickerModel],
      })

      tmp = {
        'tickers': [
          {
            'amount': '0.66075377',
            'datetime': '1517408042',
            'fee': None,
            'id': None,
            'info': '[]',
          }
        ]
      }
      result = TickerListTemplate.run(tmp)
      self.assertEqual(result['tickers'][0]['amount'], 0.66075377)
      self.assertEqual(result['tickers'][0]['datetime'], datetime(2018, 1, 31, 6, 14, 2))
      self.assertEqual(result['tickers'][0]['info'], [])
      self.assertEqual(result['tickers'][0]['fee'], None)
      self.assertEqual(len(result['tickers']), 1)
