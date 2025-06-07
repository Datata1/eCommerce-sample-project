import os
import json
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.formats.json import JsonRowDeserializationSchema


KAFKA_CONNECTOR_PATH = f"file://{os.path.dirname(os.path.realpath(__file__))}/lib/flink-sql-connector-kafka-3.0.2-1.18.1.jar"

def process_events():
    """
    Hauptfunktion zur Definition und Ausführung des PyFlink-Jobs.
    """
    # 1. Umgebung einrichten
    env = StreamExecutionEnvironment.get_execution_environment()
    # Füge den Kafka-Connector zum Classpath hinzu
    env.add_jars(KAFKA_CONNECTOR_PATH)

    # 2. Kafka als Quelle definieren
    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers("kafka:9092") \
        .set_topics("ecommerce-events") \
        .set_group_id("pyflink-event-consumer") \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(
            # Wir erwarten JSON-Strings von unserem Event-Collector
            JsonRowDeserializationSchema.builder().build()
        ) \
        .build()

    # 3. Datenstrom von der Quelle erstellen
    # Der Name ist wichtig für die Benutzeroberfläche von Flink
    stream = env.from_source(kafka_source, "Kafka Source: ecommerce-events")

    # 4. Transformation: Verarbeite jedes Event
    # Wir nehmen den JSON-Row-Typ von Flink, greifen auf das Feld 'eventType' zu
    # und wandeln es in Großbuchstaben um.
    def transform_event(event):
        # Das 'event' ist hier eine Flink-interne Row-Darstellung des JSON
        event_type = event.eventType.upper()
        return f"Verarbeiteter Event-Typ: {event_type}, Produkt: {event.productId}"

    processed_stream = stream.map(transform_event)

    # 5. Sink: Gib das Ergebnis in den TaskManager-Logs aus
    # Dies ist der einfachste Weg, um die Verarbeitung zu überprüfen.
    processed_stream.print()

    # 6. Job ausführen
    env.execute("E-Commerce Event Processor")

if __name__ == '__main__':
    process_events()