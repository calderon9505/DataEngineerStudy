# Dataflow with Java

## Requirements

Set up your development environment
1. Download and install the Java Development Kit (JDK) version 8, 11, or 17. Verify that the JAVA_HOME environment variable is set and points to your JDK installation.
    - the `java -version` indicates there is a JRE installed.
    - the `javac -version` indicates there is a JDK installed.
    - To install de JDK `sudo apt-get install default-jdk`
1. Download and install Apache Maven by following the installation guide for your operating system.
    - `sudo apt install maven`
    - `mvn -version`

[Apache Beam Java SDK quickstart](https://beam.apache.org/get-started/quickstart-java/)

It is also possible to implement in Colab [Try Apache Beam](https://beam.apache.org/get-started/try-apache-beam/)

It is easier to run the pipeline in the Cloud Shell.

## Example

```sh
mvn archetype:generate \
    -DarchetypeGroupId=org.apache.beam \
    -DarchetypeArtifactId=beam-sdks-java-maven-archetypes-examples \
    -DarchetypeVersion=2.41.0 \
    -DgroupId=org.example \
    -DartifactId=word-count-beam \
    -Dversion="0.1" \
    -Dpackage=org.apache.beam.examples \
    -DinteractiveMode=false
   ```

Run with direct-runner

```sh
mvn compile exec:java -Dexec.mainClass=org.apache.beam.examples.WordCount -Dexec.args="--inputFile=sample.txt --output=counts" -Pdirect-runner
```

Run with Dataflow

```sh
mvn compile exec:java -Dexec.mainClass=org.apache.beam.examples.WordCount \
    -Dexec.args="--runner=DataflowRunner --project=<your-gcp-project> \
                 --region=<your-gcp-region> \
                 --gcpTempLocation=gs://<your-gcs-bucket>/tmp \
                 --inputFile=gs://apache-beam-samples/shakespeare/* --output=gs://<your-gcs-bucket>/counts" \
    -Pdataflow-runner
```

# my projects

`ln -s /mnt/c/Users/User/Documents/DataScience_Platzi/10_Cloud/GCP/Dataflow/java/ java_beam`

He decidido correr los pipelines en el Cloud Shell, porque no encontré cómo hacerlo facil en mi máquina local. Crear la siguiente estructura de carpetas.

```
.
├── pom.xml
└── src
    └── main
        └── java
            └── MinimalWordCount.java
```

Para compilar 
```sh
mvn compile exec:java -Dexec.mainClass=MinimalWordCount -Pdirect-runner
```
