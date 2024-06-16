import unittest
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to
from process_transaction import prepData, ProcessTransformations

class Test(unittest.TestCase):
    def test_process(self):
        input_data = [
            '2011-01-01 02:54:25 UTC,wallet010,wallet010,30.00\n',
            '2009-12-31 02:54:25 UTC,wallet010,wallet010,50.00\n',
            '2012-05-14 02:54:25 UTC,wallet010,wallet010,25.00\n',
            '2013-07-18 02:54:25 UTC,wallet010,wallet010,15.00\n',
            '2010-08-10 02:54:25 UTC,wallet010,wallet010,45.00\n'
        ]

        expected_output = [
            ('2011-01-01', 30.0),
            ('2012-05-14', 25.0),
            ('2010-08-10', 45.0)
        ]

        with TestPipeline() as p:
            processedData = (
                    p
                    | "Create Input" >> beam.Create(input_data)
                    | "Parse Lines" >> beam.ParDo(prepData())
                    | "Filter Transactions & Extract Date and Amount" >> ProcessTransformations()
            )

            assert_that(processedData, equal_to(expected_output))

if __name__ == '__main__':
    unittest.main()