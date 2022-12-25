import argparse
import json

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from beam_nuggets.io import kafkaio
from google.cloud import bigquery
from google.oauth2 import service_account
from jsonpath_ng import jsonpath, parse

# from apache_beam.io.gcp.internal.clients import bigquery


class findTable(beam.DoFn):
    def __init__(self, df):
        self.df = df

    def process(self, element):
        # print(self.df)
        message = json.loads(element)
        for index, path_clasificacion in enumerate(self.df['path_clasificacion']):
            # print(path)
            path = path_clasificacion.split('=')[0]
            value = path_clasificacion.split('=')[1].strip().replace("'","")

            jsonpath_expression = parse('$.'+path)
            match = jsonpath_expression.find(message)
            # print('valor 1:',value)
            # print('valor 2:',match[0].value)
            if value == match[0].value:
                # print(self.df.loc[index, 'tabla'])
                return self.df.loc[index,'tabla'], element
            # return [match[0].value]
                

def get_metadata():
    credentials_file = 'wb-streaming.json'
    project_id = 'wb-streaming'
    credentials = service_account.Credentials.from_service_account_file(credentials_file)
    client = bigquery.Client(credentials= credentials,project=project_id)

    query_maestra = "select estructura, path_clasificacion, base_datos, tabla \
            from test1.metadata_maestra_json \
            where identificador = 'MBAAS_TEST_DATAFLOW' \
            and estado = 'Activo'"
    metadata_maestra = client.query(query_maestra).to_dataframe()

    print("'"+"','".join(metadata_maestra['estructura'].tolist())+"'")
    estructuras = "'"+"','".join(metadata_maestra['estructura'].tolist())+"'"
    query_estructuras = f"select paths, nombre_columna, tipo_dato \
            from test1.metadata_estructuras_json \
            where estructura in ({estructuras})"
    metadata_estructuras = client.query(query_estructuras).to_dataframe()

    return metadata_maestra

def run_pipeline(custom_args, beam_args):

    metadata_maestra = get_metadata()

    ##################### Configuracion kafka
    consumer_config = {
                    "bootstrap_servers": "localhost:9092",
                    "topic": "reinyeccion_test",
                    }

    input_file = custom_args.file
    opts = PipelineOptions(beam_args)
    with beam.Pipeline(options=opts) as p:

        # messages = p | kafkaio.KafkaConsume(consumer_config=consumer_config)
        # messages | beam.Map(print)

        lines = (
            p 
            | beam.io.ReadFromText(input_file)
            | beam.ParDo(findTable(metadata_maestra))
            # | beam.combiners.Count.Globally()
            # | beam.Map(print)
            )  
        

def main():
    parser = argparse.ArgumentParser(description="Read and structure a JSON file")
    parser.add_argument("--file", help="Fichero de entrada")

    custom_args, beam_args = parser.parse_known_args()
    run_pipeline(custom_args, beam_args)


if __name__ == '__main__':
    main()


# pip install beam-nuggets
# https://github.com/mohaseeb/beam-nuggets
# https://github.com/mohaseeb/beam-nuggets/blob/master/beam_nuggets/io/kafkaio.py#L4
# http://mohaseeb.com/beam-nuggets/beam_nuggets.io.kafkaio.html

# pip install jsonpath-ng
# https://www.digitalocean.com/community/tutorials/python-jsonpath-examples

# pip install apache_beam[dataframe]
# https://beam.apache.org/documentation/dsls/dataframes/overview/

# cp /mnt/c/Users/User/Documents/DataScience_Platzi/10_Cloud/GCP/Dataflow/python/read_json/read_json.py /home/calderon/read_json/

'''
select * from `test1.metadata_maestra_json`
where identificador = 'MBAAS_TEST_DATAFLOW';
'''

'''
INSERT INTO `test1.metadata_maestra_json`
(id_parametrizacion, identificador, estructura, path_clasificacion, base_datos, tabla,estado)
values(
  '202209271032',
  'MBAAS_TEST_DATAFLOW',
  'MBAAS_TEST_OPERACION',
  "jsonPayload.msm='AUDITORIA: Operaciones'",
  'test1',
  'mbaas_log_operacional',
  'Activo'
  );
'''

'''
select * from `test1.metadata_maestra_json`
where identificador = 'MBAAS_TEST_DATAFLOW';

select * from `test1.metadata_estructuras_json`
where estructura in ("MBAAS_GENERAL_V1_OPE")
order by id_parametrizacion;
'''


'''
cd .\10_Cloud\GCP\Dataflow\python\read_json\
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate
'''