import unittest
from morphit import Processor, Parser, Types
from datetime import datetime, timezone, time

class TestProcessor(unittest.TestCase):
    def test_processor(self):
        p = Processor(int)
        self.assertEqual(p('1.0'), 1)

    def test_processor_dt(self):
        p = Processor(Types['Date'])
        self.assertEqual(p(1576226168.818243), datetime(2019, 12, 13, 0, 36, 8, 818243))

    def test_processor_arr(self):
        p = Processor([Types['Date']])
        self.assertEqual(p([1576226168.818243]), [datetime(2019, 12, 13, 0, 36, 8, 818243)])

    def test_processor_obj(self):
        p = Processor({
          'start': Types['Date'],
          'end': Types['Date'],
        })
        result = p({
          'start': 1576226168.818243,
          'end': 1576226168.818243,
        })
        expected = {
          'start': datetime(2019, 12, 13, 0, 36, 8, 818243),
          'end': datetime(2019, 12, 13, 0, 36, 8, 818243),
        }
        self.assertEqual(result, expected)

    def test_processor_obj_deep(self):
        p = Processor({
          'deep':{
            'start': Types['Date'],
            'end': Types['Date'],
          }
        })
        childProcessor = Processor({
          'start': Types['Date'],
          'end': Types['Date'],
        })

        p3 = Processor({'deep': childProcessor })
        p4 = Processor([p3])
        tmp = {
          'deep':{
            'start': 1576226168.818243,
            'end': 1576226168.818243,
          }
        }
        resultFull = p(tmp)
        resultNested = p3(tmp)
        resultNestedArr = p4([tmp])
        expected = {
          'deep':{
            'start': datetime(2019, 12, 13, 0, 36, 8, 818243),
            'end': datetime(2019, 12, 13, 0, 36, 8, 818243),
          }
        }
        self.assertEqual(resultNested, expected)
        self.assertEqual(resultFull, expected)
        self.assertEqual(resultNestedArr, [expected])


    def test_processor_chain_then(self):
        p = Processor(float)
        self.assertEqual(p('1.0'), 1.0)
        p.then(int)
        self.assertEqual(p('1.0'), 1)

    def test_processor_chain_flow(self):
        p = Processor.flow([float, int])
        self.assertEqual(p('1.0'), 1)
        # Base case of 1 elem
        p = Processor.flow([int])
        self.assertEqual(p('1.0'), 1)

    def test_processor_chain_complex(self):
        p = Processor.flow([float, int, lambda x: x*34])
        self.assertEqual(p('1.0'), 34)

    def test_processor_chain_complex(self):
        p0=Processor(lambda partial, options={}: '%s -> %s'%(options, partial*34))
        p = Processor.flow([float, int, lambda partial, options={}: '%s -> %s'%(options, partial*34)])
        self.assertEqual(p('1.0'), '1.0 -> 34')

    def test_processor_chain_lambda_original_value(self):
        p0=Processor(lambda partial, options={}: '%s -> %s'%(options, partial*34))
        partA = lambda partial, options={}: {'total': sum(partial)}
        def partB(partial, options={}):
          partial.update({'fraction': options[1]/partial['total']})
          return partial
        p = Processor.flow([partA,partB])
        res=p([10,2,100])
        exp={'total':112, 'fraction': 2/112}
        self.assertEqual(exp['fraction'], res['fraction'])
        self.assertEqual(exp['total'], res['total'])
