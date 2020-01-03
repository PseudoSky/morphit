import unittest
from morphit import Processor, Parser, Instances, Aggregators
from datetime import datetime, timezone, time

class TestProcessor(unittest.TestCase):
    def test_processor(self):
        p = Processor(int)
        self.assertEqual(p('1.0'), 1)

    def test_processor_dt(self):
        p = Processor(Instances['datetime'])
        self.assertEqual(p(1576226168.818243), datetime(2019, 12, 13, 0, 36, 8, 818243))

    def test_processor_arr(self):
        p = Processor([Instances['datetime']])
        self.assertEqual(p([1576226168.818243]), [datetime(2019, 12, 13, 0, 36, 8, 818243)])

    def test_processor_obj(self):
        p = Processor({
          'start': Instances['datetime'],
          'end': Instances['datetime'],
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
            'start': Instances['datetime'],
            'end': Instances['datetime'],
          }
        })
        childProcessor = Processor({
          'start': Instances['datetime'],
          'end': Instances['datetime'],
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

    def test_processor_aggs(self):
        self.assertEqual(Instances['lambda'](1), 1)
        self.assertEqual(Aggregators['map']([None, 1,2,3]), [1,2,3])
        self.assertEqual(Aggregators['reduce']([None, 1,2,3]), 3)
        self.assertEqual(Aggregators['merge']([None, {}, {'a':1}, {'b':2}]), {'a':1,'b':2})

    def test_custom_processor_aggs(self):
        getLastResult = lambda res: res[-1]['result']
        proc = Processor(lambda p, options={}: {'result':[1,2,3]}, aggregator=getLastResult)
        self.assertEqual(proc(None), [1,2,3])


    def test_processor_chain_lambda_original_value(self):
        partA = lambda partial, options={}: {'total': sum(partial)}
        def partB(partial, options={}):
          partial.update({'fraction': options[1]/partial['total']})
          return partial
        def partC(partial, options={}):
          return {'fraction': options[1]/partial['total']}
        pReduce = Processor.flow([partA, partC], aggregator='reduce')
        pReduceMerge = Processor.flow([partA, partB], aggregator='reduce')
        pMerge = Processor.flow([partA,partC], aggregator='merge')
        resultReduce=pReduce([10,2,100])
        resultReduceMerge=pReduceMerge([10,2,100])
        resultMerge=pMerge([10,2,100])
        exp={'total':112, 'fraction': 2/112}
        self.assertEqual({'fraction': 2/112}, resultReduce)
        self.assertEqual(exp, resultReduceMerge)
        self.assertEqual(exp, resultMerge)
        self.assertEqual(resultReduceMerge, resultMerge)
