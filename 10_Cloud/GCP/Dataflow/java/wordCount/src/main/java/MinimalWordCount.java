import java.util.Arrays;
import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.io.TextIO;
import org.apache.beam.sdk.options.PipelineOptions;
import org.apache.beam.sdk.options.PipelineOptionsFactory;
import org.apache.beam.sdk.transforms.Count;
import org.apache.beam.sdk.transforms.Filter;
import org.apache.beam.sdk.transforms.FlatMapElements;
import org.apache.beam.sdk.transforms.MapElements;
import org.apache.beam.sdk.values.KV;
import org.apache.beam.sdk.values.TypeDescriptors;

public class MinimalWordCount{
    
    public static void main(String[] args){

        PipelineOptions options = PipelineOptionsFactory.create();
        Pipeline p = Pipeline.create(options);

        // convierte archivo en PCollection donde cada elemento es una linea de texto
        p.apply(TextIO.read().from("gs://apache-beam-samples/shakespeare/kinglear.txt"))
            // separa cada linea en palabras
            .apply(
                FlatMapElements.into(TypeDescriptors.strings())
                    .via((String line) -> Arrays.asList(line.split("[^\\p{L}]+"))))
            // filtrar palabras vacias
            .apply(Filter.by((String word) -> !word.isEmpty()))
            // contar palabras
            .apply(Count.perElement())
            // convierte de KV a string para imprimir
            .apply(
                MapElements.into(TypeDescriptors.strings())
                    .via(
                        (KV<String, Long> wordCount) ->
                            wordCount.getKey() + ": " + wordCount.getValue()))
            // convierte el PCollection a un archivo
            .apply(TextIO.write().to("wordcounts"));

        p.run().waitUntilFinish();
    }
}
