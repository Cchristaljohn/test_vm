import apache_beam as beam
from datetime import datetime
from apache_beam.options.pipeline_options import PipelineOptions
import json


class prepData(beam.DoFn):
    def process(self, element):
        rows = element.split(",")
        return [{
            'timestamp': rows[0],
            'transaction_amount': float(rows[3])
        }]


class filterData(beam.DoFn):
    def process(self, element):
        transaction_date = datetime.strptime(element['timestamp'], '%Y-%m-%d %H:%M:%S %Z')
        if element['transaction_amount'] > 20 and transaction_date.year >= 2010:
            return [(transaction_date.strftime('%Y-%m-%d'), element['transaction_amount'])]


class ProcessTransformations(beam.PTransform):
    def expand(self, pcoll):
        return (pcoll
                | beam.ParDo(filterData())
                | beam.CombinePerKey(sum)
                )


class prepJSONL(beam.DoFn):
    def process(self, element):
        return [json.dumps({'date': element[0], 'total_amount': element[1]})]


def run():
    input_file = 'gs://cloud-samples-data/bigquery/sample-transactions/transactions.csv'
    output_file = 'output/results'

    pipeline_options = PipelineOptions()
    with beam.Pipeline(options=pipeline_options) as p:
        (
                p
                | beam.io.ReadFromText(input_file, skip_header_lines=1)
                | beam.ParDo(prepData())
                | ProcessTransformations()
                | beam.ParDo(prepJSONL())
                | beam.io.WriteToText(output_file,file_name_suffix='.jsonl.gz')
        )


if __name__ == '__main__':
    run()
