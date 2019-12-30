"""
morphit tests.
"""

import unittest
from morphit import Parser, Processor, Types
from datetime import datetime, timezone, time

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

    def test_none(self):
      pt = Processor({
        'amount': 0.66075377,
        'datetime': Types['Date'],
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
      self.assertEqual(pt(tmp), tmp)

    '''
    Test Date Parsing
    '''

    def test_string_float_ts(self):
      # Parse ms timestamp format (like from python)
      pt = Processor(Types['Date'])
      tmp ='1517408042.277897'
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2, 277897), pt(tmp))
      tmp ='1517408042'
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2), pt(tmp))

    def test_s_ts(self):
      # Parse ms timestamp format (like from python)
      pt = Processor(Types['Date'])
      tmp = 1517408042.277897
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2, 277897), pt(tmp))
      tmp = 1517408042
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2), pt(tmp))



    def test_string_ms_ts(self):
      # Parse s timestamp format (like from python)
      pt = Processor(Types['Date'])
      tmp ='1517408265547'
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), pt(tmp))


    def test_ms_ts(self):
      # Parse s timestamp format (like from python)
      pt = Processor(Types['Date'])
      tmp = 1517408265547
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), pt(tmp))

    def test_json_dump_datetime(self):
      # Test the json datetime encoder
      pt = Processor(Types['Date'])
      tmp = pt(1517408265547)
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), tmp)
      res = Parser('', {'datetime': tmp})
      self.assertEqual('{"datetime": "2018-01-31T06:17:45.547"}', res)

    def test_datetime_to_int_cast(self):
      # Test the timestamp encoding a datetime to int
      pt = Processor(int)
      tmp = pt(datetime(2018, 1, 31, 6, 17, 45, 547000))
      self.assertEqual(1517408265547, tmp)

    def test_datetime_to_float_cast(self):
      # Test encoding a datetime to a float
      pt = Processor(float)
      tmp = pt(datetime(2018, 1, 31, 6, 14, 2, 277897))
      self.assertEqual(1517408042.277897, tmp)

    def test_datetime_to_str_cast(self):
      # Test encoding a datetime to a float
      pt = Processor(str)
      tmp = pt(datetime(2018, 1, 31, 6, 17, 45, 547000))
      self.assertEqual("2018-01-31T06:17:45.547", tmp)

    def test_lambda_conversion(self):
      # Executes the lambda passed in rather than using builtin
      pt = Processor(lambda x: int(x)*10)
      self.assertEqual(10, pt('1'))

    def test_function_conversion(self):
      # Executes the function passed in rather than using builtin
      def convert_multiply(var): return int(var)*10
      pt = Processor(convert_multiply)
      self.assertEqual(10, pt('1'))

    def test_nested_parser_template(self):
      TickerModel = Processor({
        'amount': 0.66075377,
        'datetime': Types['Date'],
        'fee': None,
        'id': None,
        'info': ['659.100000', '0.66075377', 1517364874.3597, 's', 'l', ''],
      })

      TickerListProcessor = Processor({
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
      result = TickerListProcessor(tmp)
      self.assertEqual(result['tickers'][0]['amount'], 0.66075377)
      self.assertEqual(result['tickers'][0]['datetime'], datetime(2018, 1, 31, 6, 14, 2))
      self.assertEqual(result['tickers'][0]['info'], [])
      self.assertEqual(result['tickers'][0]['fee'], None)
      self.assertEqual(len(result['tickers']), 1)
