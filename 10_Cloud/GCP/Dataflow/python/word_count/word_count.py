import apache_beam as beam
from apache_beam import PCollection
from apache_beam.options.pipeline_options import PipelineOptions

import argparse # Leer argumentos desde la linea de comandos
from typing import Tuple


def sanitizar_palabra(palabra):
  para_quitar = [',', '.', '-', ':', ' ', "'", '"']

  for simbolo in para_quitar:
    palabra = palabra.replace(simbolo, '')

  palabra = palabra.lower()

  palabra = palabra.replace("á", "a")
  palabra = palabra.replace("é", "e")
  palabra = palabra.replace("í", "i")
  palabra = palabra.replace("ó", "o")
  palabra = palabra.replace("ú", "u")

  return palabra


def main():
  parser = argparse.ArgumentParser(description="Nuestro primer pipeline")
  parser.add_argument("--entrada", help="Fichero de entrada")
  parser.add_argument("--salida", help="Fichero de salida")
  parser.add_argument("--n-palabras", type=int, help="Número de palabras en la salida")

  # distinguir los argumentos de python y los de apache beam
  our_args, beam_args = parser.parse_known_args()
  run_pipeline(our_args, beam_args)


def run_pipeline(custom_args, beam_args):
  entrada = custom_args.entrada
  salida = custom_args.salida
  n_palabras = custom_args.n_palabras

  opts = PipelineOptions(beam_args)

  with beam.Pipeline(options=opts) as p:
    lineas: PCollection[str] = p | "Leemos entrada" >> beam.io.ReadFromText(entrada)
    # Partir cada linea en sus palabras
    # Map devuelve una lista, FlatMap quita esa lista y devuelve cada string por aparte
    palabras = lineas | "Pasamos a palabras" >> beam.FlatMap(lambda l: l.split())
    limpiadas = palabras | "Sanitizamos" >> beam.Map(sanitizar_palabra)
    contadas: PCollection[Tuple[str, int]] = limpiadas  | "Contamos" >> beam.combiners.Count.PerElement()
    # "En" -> ("En", 17)
    # "un" -> ("un", 28)
    palabras_top_lista = contadas | "Ranking" >> beam.combiners.Top.Of(n_palabras, key=lambda kv: kv[1])
    palabras_top = palabras_top_lista | "Desenvuelve lista" >> beam.FlatMap(lambda x: x)
    formateado: PCollection[str] = palabras_top | "Formateamos" >> beam.Map(lambda kv: "%s,%d" % (kv[0], kv[1]))
    formateado | "Escribimos salida" >> beam.io.WriteToText(salida)


if __name__ == '__main__':
  main()


