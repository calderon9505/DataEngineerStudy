kedro new --name=<your-project-name> --tools=<your-project-tools> --example=<yes/no>

kedro new --name=spaceflights --tools=lint,test,log,data --example=no

kedro new --name=no-tools --tools=none --example=no



kedro pipeline create data_processing
kedro registry list
kedro run --pipeline data_processing
kedro viz

kedro pipeline create data_science
kedro run
kedro viz

kedro run --pipeline data_processing --env=test

kedro package
en nuevo ambiente
pip install C:/Users/sebastian.calderon/Documents/GitHub/work/kedro/spaceflights/dist/spaceflights-0.1-py3-none-any.whl
al instalar de esta forma, me aparece spaceflights como un paquete más de python
python -m spaceflights --conf-source=C:/Users/sebastian.calderon/Documents/GitHub/work/kedro/spaceflights/dist/conf-spaceflights.tar.gz --env=DS

kedro docker init
kedro docker build --base-image python:3.10-slim
kedro docker run


# Kedro-MLflow

https://docs.kedro.org/en/1.2.0/integrations-and-plugins/mlflow/#tracking-kedro-in-mlflow-using-the-python-api

instalar el hook para mlfow, esto es, la librería kedro-mlflow
crear el archivo mlflow.yml con el endpoint al que debe apuntar