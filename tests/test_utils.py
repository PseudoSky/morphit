"""
nix tests.
"""

import unittest
from nix.utils import Parser, ParserTemplate
from datetime import datetime
class TestUtils(unittest.TestCase):
    """
    Test nix's utils.
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

    def test_none(self):
      pt = ParserTemplate({
        'amount': 0.66075377,
        'datetime': ParserTemplate.types['Date'],
        'fee': None,
        'id': None,
        'info': ['659.100000', '0.66075377', 1517364874.3597, 's', 'l', ''],
      })

      tmp ={
        'amount': 0.66075377,
        'datetime': '2018-01-31T02:14:34.359Z',
        'fee': None,
        'id': None,
        'info': ['659.100000', '0.66075377', 1517364874.3597, 's', 'l', ''],
      }
      self.assertEqual(pt.run(tmp), tmp)


    '''
    Test Date Parsing
    '''

    def test_string_float_ts(self):
      # Parse ms timestamp format (like from python)
      pt = ParserTemplate(ParserTemplate.types['Date'])
      tmp ='1517408042.277897'
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2, 277897), pt.run(tmp))
      tmp ='1517408042'
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2), pt.run(tmp))

    def test_s_ts(self):
      # Parse ms timestamp format (like from python)
      pt = ParserTemplate(ParserTemplate.types['Date'])
      tmp =1517408042.277897
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2, 277897), pt.run(tmp))
      tmp =1517408042
      self.assertEqual(datetime(2018, 1, 31, 6, 14, 2), pt.run(tmp))



    def test_string_ms_ts(self):
      # Parse s timestamp format (like from python)
      pt = ParserTemplate(ParserTemplate.types['Date'])
      tmp ='1517408265547'
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), pt.run(tmp))


    def test_ms_ts(self):
      # Parse s timestamp format (like from python)
      pt = ParserTemplate(ParserTemplate.types['Date'])
      tmp =1517408265547
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), pt.run(tmp))

    def test_json_dump_datetime(self):
      # Test the json datetime encoder
      pt = ParserTemplate(ParserTemplate.types['Date'])
      tmp = pt.run(1517408265547)
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000), tmp)
      res = Parser('', {'datetime': tmp})
      self.assertEqual('{"datetime": "2018-01-31T06:17:45.547"}', res)