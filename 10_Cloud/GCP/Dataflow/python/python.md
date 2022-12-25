# Dataflow with Python

[**Paso a paso para nuestro primer pipeline con Apache Beam y Dataflow**](https://www.youtube.com/watch?v=xSgTsKWhU0Y&ab_channel=SoftwareGuru)

[Apache Beam Python SDK Quickstart](https://beam.apache.org/get-started/quickstart-py/)

[Apache Beam WordCount Examples](https://beam.apache.org/get-started/wordcount-example/#wordcount-example)

Crear archivo .py

crear ambiente virtual y activarlo

```sh
cd .\10_Cloud\GCP\Dataflow\python\word_count\
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\activate
```

```sh
py -m pip install --upgrade pip
pip install apache-beam
pip install 'apache-beam[gcp]'
```
opcional
```
pip install apache_beam[dataframe]
```

Para ejecutar el código en local se usa `--runner DirectRunner`, aunque este es el valor por defecto.

```sh
py word_count.py --n-palabras 500 --entrada el_quijote.txt --salida output.csv
```

El mismo código se puede ejecutar tanto en Spark, Flink o Dataflow.

Para ejecutar en Dataflow

```sh
gcloud config set ace-thought-348115
gcloud config set account calderon950527@gmail.com
gcloud auth login
gsutil cp .\el_quijote.txt gs://test_my_first_dataflow/
```

El dataflow requiere un directorio temporal para su funcionamiento

```sh
py word_count.py --n-palabras 500 --entrada gs://test_my_first_dataflow/el_quijote.txt --salida gs://test_my_first_dataflow/output.csv --runner DataflowRunner --project ace-thought-348115 --region us-east1 --temp_location gs://test_my_first_dataflow/tmp/
```