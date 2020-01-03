import unittest
import json
from morphit import Processor, Parser, JSONEncoder, Instances
from datetime import datetime, timezone, time, timezone, date

class TestParser(unittest.TestCase):
    def setUp(self):
      self.template = {
          'dict':dict,
          'tojson':str,
          'tupletojson': (str,),
          'this':float,
          'other':2.0,
          'that': bool,
      }
    def test_none_to_int_float(self):
      # Executes the function passed in rather than using builtin
      float_t = Parser(1.0, None)
      int_t = Parser(1, None)
      self.assertEqual(float_t, 0.0)
      self.assertEqual(int_t, 0)
      self.assertEqual(Instances['datetime'],datetime(2019, 12, 6, 20, 31, 59, 329921))

    def test_case_float_string_to_int(self):
        res = Parser(60, '150.0')
        self.assertEqual(res, 150)
        res = Parser(90, '0.0')
        self.assertEqual(res, 0)
        res = Parser(90, '.0')
        self.assertEqual(res, 0)

    def test_json_to_array(self):
        case = "[\"earthofficial\", \"blackandwhite\", \"worldshotz\"]"
        res = Parser([], case)
        self.assertEqual(res, ["earthofficial", "blackandwhite", "worldshotz"])

    def test_str_to_array(self):
        case = "['photo', 'photos', 'pic', 'pics']"
        res = Parser([], case)
        self.assertEqual(res, ['photo', 'photos', 'pic', 'pics'])

    def test_untyped_str_to_array(self):
        case = "['photo', 2, 'pic', 'pics']"
        res = Parser([], case)
        self.assertEqual(res, ['photo', 2, 'pic', 'pics'])

    def test_typed_str_to_array(self):
        case = "['photo', 2, 'pic', 'pics']"
        res = Parser(['strings'], case)
        self.assertEqual(res, ['photo', '2', 'pic', 'pics'])

    def test_str_no_brackets_to_array(self):
        case = "photo"
        res = Parser([], case)
        self.assertEqual(res, ['photo'])

    def test_unicode_to_array(self):
      res = Parser([], "[u'this',u'that']")
      self.assertEqual(res, ['this','that'])

    def test_string_bad_int_to_float(self):
      self.assertRaises(ValueError, Parser, 2.0, 'MMMM')

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

    '''
    Test Date Parsing
    '''

    def test_datetime_to_float(self):
      dt = datetime(2019, 12, 6, 20, 31, 59, 329921)
      tmp = Parser(float, dt)
      self.assertEqual(1575693119.329921, tmp)

    def test_str_float_to_datetime(self):
      dt = "1575693119.329921"
      tmp = Parser(datetime(2019, 12, 6, 20, 31, 59, 329921), dt)
      self.assertEqual(datetime(2019, 12, 6, 20, 31, 59, 329921), tmp)

    def test_float_to_datetime(self):
      dt = datetime(2019, 12, 6, 20, 31, 59, 329921)
      tmp = Parser(dt, 1575693119.329921)
      self.assertEqual(dt, tmp)

    def test_datetime_to_int(self):
      dt = datetime(2019, 12, 6, 20, 31, 59, 329000)
      tmp = Parser(int, dt)
      self.assertEqual(1575693119329, tmp)

    def test_int_to_datetime(self):
      dt = datetime(2019, 12, 6, 20, 31, 59, 329000)
      tmp = Parser(dt, 1575693119329)
      self.assertEqual(dt, tmp)

    def test_str_to_datetime(self):
      tmp = datetime(2018, 1, 31, 6, 17, 45, 547000)
      res = Parser(tmp, "2018-01-31T06:17:45.547")
      self.assertEqual(res, tmp)

    def test_datetime_time_to_str(self):
      res = Parser(str, time(6,17, 45, 547000))
      self.assertEqual('06:17:45.547', res)
      res = Parser(str, time(6,17, 45))
      self.assertEqual('06:17:45', res)
      self.assertRaises(ValueError, Parser, '', time(6,17, 45, tzinfo=timezone.utc))




    def test_str_to_datetime(self):
      res = Parser(datetime(2018, 1, 31, 6, 17, 45, 547000), "2018-01-31T06:17:45.547")
      self.assertEqual(datetime(2018, 1, 31, 6, 17, 45, 547000, tzinfo=timezone.utc), res)


    def test_isoutc_str_to_datetime(self):
      res = Parser('2018-01-31T06:17:45.547000+00:00', datetime(2018, 1, 31, 6, 17, 45, 547000, tzinfo=timezone.utc))
      self.assertEqual('2018-01-31T06:17:45.547Z', res)

    def test_isoutc_str_microsec_to_datetime(self):
      tst = datetime(2018, 1, 31, 6, 17, 45, microsecond=547134)
      res = Parser('2018-01-31T06:17:45.547000+00:00', tst)
      self.assertEqual('2018-01-31T06:17:45.547', res)


    def test_isoutc_str_microsec_to_datetime(self):
      tst = datetime(2018, 1, 31, 6, 17, 45, tzinfo=timezone.utc)
      res = Parser('2018-01-31T06:17:45.547+00:00', tst)
      self.assertEqual('2018-01-31T06:17:45Z', res)

    def test_isoutc_str_microsec_utc_to_datetime(self):
      tst = datetime(2018, 1, 31, 6, 17, 45, microsecond=547134, tzinfo=timezone.utc)
      res = Parser('2018-01-31T06:17:45.547000+00:00', tst)
      self.assertEqual('2018-01-31T06:17:45.547Z', res)

    def test_date_to_str(self):
      res = Parser('2018-01-31T06:17:45.547000+00:00', date(2018, 1, 31))
      self.assertEqual('2018-01-31', res)

    def test_str_to_date(self):
      res = Parser(date(2018, 1, 31), '2018-01-31')
      self.assertEqual(date(2018, 1, 31), res)

    def test_time_to_str(self):
      res = Parser('', time(15, 24, 46, 209647))
      self.assertEqual('15:24:46.209', res)

    def test_dict_to_json(self):
      res = Parser('', {'a': { 'b': 123456 }})
      self.assertEqual('{"a": {"b": 123456}}', res)

    def test_special_case_to_json(self):
      res1 = Parser('', {'a': (123456,)})
      res2 = Parser('', (123456,))
      res3 = Parser('', [123456])
      res4 = Parser('', [datetime(2018, 1, 31, 6, 17, 45, 547000)])
      self.assertEqual(res1, '{"a": [123456]}')
      self.assertEqual(res2, '[123456]')
      self.assertEqual(res3, '[123456]')
      self.assertEqual(res4, '["2018-01-31T06:17:45.547"]')

    def test_json_encoder_date_resolve(self):
      res = json.dumps(datetime(2018, 1, 31, 6, 17, 45, 547000), cls=JSONEncoder)
      self.assertEqual(res, '"2018-01-31T06:17:45.547"')

    def test_json_encoder_lambda_resolve(self):
      res = json.dumps({'date': lambda: datetime(2018, 1, 31, 6, 17, 45, 547000)}, cls=JSONEncoder)
      self.assertEqual(res, '{"date": "2018-01-31T06:17:45.547"}')

    def test_json_encoder_processor_resolve(self):
      res = json.dumps({'date': Processor(datetime(2018, 1, 31, 6, 17, 45, 547000))}, cls=JSONEncoder)
      self.assertEqual(res, '{"date": null}')

    def test_fallback_default(self):
      res = Parser(object, None)
      self.assertEqual(res, None)

    def test_fallback_custom(self):
      res = Parser(object, None, 100)
      self.assertEqual(res, 100)

    def test_none_base(self):
      res = Parser(None, 100)
      self.assertEqual(res, 100)


    def test_parse_nested_objects(self):
        res = Parser(self.template, "{u'dict':{u'check':u'yup'}, u'tojson':{u'check':u'yup'}, 'tupletojson':[9,9], u'this':u'2.0','other': '2', 'that':'False'}")
        self.assertEqual(type(res),type({}))
        self.assertEqual(type(res['that']), type(False))
        self.assertEqual(res['that'], False)
        self.assertEqual({'check': 'yup'}, res['dict'])
        self.assertEqual('{\"check\": \"yup\"}', res['tojson'])
        self.assertEqual(('9', '9'), res['tupletojson'])

    '''
    Fancier nesting cases
    '''


    def test_flat_array(self):
      tmp = [659.100000, 0, '1.0', 1, 's', 'l', '']
      test = ['659.100000', '', 1.0, '1.0']
      res = Parser(tmp, test)
      self.assertEqual(res, [659.100000, 0, '1.0', 1])

    def test_flat_array(self):
      tmp = []
      test = ('659.100000', '', 1.0, '1.0')
      res = Parser(tmp, test)
      self.assertEqual(res, ['659.100000', '', 1.0, '1.0'])


    def test_deep_array(self):
      tmp = [{ 'deep_bool': True, 'deep_float': 1.0 }]
      test = ["{ 'deep_bool': true, 'deep_float': \"1.0\" }"]
      res = Parser(tmp, test)
      self.assertEqual(res[0]['deep_bool'], True)
      self.assertEqual(res[0]['deep_float'], 1.0)
      self.assertEqual(len(res), 1)
      self.assertEqual(len(res[0].keys()), 2)

    def test_deep_dict(self):
      tmp = {'a': {'b':3.0}}
      test = {'a': {'b': '3'}}
      res = Parser(tmp, test)
      self.assertEqual(res['a']['b'], 3.0)

    def test_deep_dict_non_matching(self):
      tmp = {'c': {'b':3.0}}
      test = {'a': {'b': '3'}}
      res = Parser(tmp, test)
      self.assertEqual(res['a']['b'], '3')


    def test_primitive_to_arr_deep_cast(self):
      tmp = {'a':[1.0], 'b':(1.0)}
      test = {'a':1000, 'b':1000}
      res = Parser(tmp, test)
      self.assertEqual(res['a'], [1000.0])
      self.assertEqual(res['b'], (1000.0))
