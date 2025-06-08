import os
import json
import sys
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common import Configuration # WICHTIGER NEUER IMPORT

def process_events():
    """
    Hauptfunktion zur Definition und Ausführung des PyFlink-Jobs.
    Die JAR-Abhängigkeiten werden über die FLINK_HOME Umgebungsvariable gesetzt.
    """
    # --- HIER IST DIE ENDGÜLTIGE LÖSUNG ---
    # 1. Erstelle ein Konfigurationsobjekt
    config = Configuration()
    # 2. Setze den Pfad zum Python-Interpreter in DIESEM Objekt.
    #    sys.executable gibt immer den Pfad zum aktuell laufenden Interpreter zurück.
    config.set_string("python.executable", sys.executable)

    config.set_string("rest.bind-address", "0.0.0.0")

    config.set_string("rest.adress", "https://67705-3000.2.codesphere.com/")

    # 3. Übergebe die Konfiguration bei der Erstellung der Umgebung.
    env = StreamExecutionEnvironment.get_execution_environment(config)
    
    # 2. Kafka als Quelle definieren - MIT SSL
    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers("ws-server-67705-kafka.workspaces:9093") \
        .set_topics("ecommerce-events") \
        .set_group_id("pyflink-event-consumer") \
        .set_starting_offsets(KafkaOffsetsInitializer.latest()) \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .set_property("security.protocol", "SSL") \
        .set_property("ssl.truststore.location", "/home/user/app/certs/kafka.client.truststore.jks") \
        .set_property("ssl.truststore.password", "meinPasswort") \
        .build()

    # 3. Datenstrom von der Quelle erstellen
    stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="Kafka Source: ecommerce-events"
    )

    # 4. Transformation: Verarbeite jedes Event
    def transform_event(event_string):
        try:
            event_dict = json.loads(event_string)
            event_type = event_dict.get("eventType", "UNKNOWN").upper()
            product_id = event_dict.get("productId", "N/A")
            return f"Verarbeiteter Event-Typ: {event_type}, Produkt: {product_id}"
        except json.JSONDecodeError as e:
            return f"Fehler beim Parsen von JSON: {e}, Event-String: {event_string}"
        except Exception as e:
            return f"Allgemeiner Fehler bei der Transformation: {e}, Event: {event_string}"

    processed_stream = stream.map(transform_event)

    # 5. Sink: Gib das Ergebnis in den Logs aus
    processed_stream.print()

    # 6. Job ausführen
    env.execute("E-Commerce Event Processor")

if __name__ == '__main__':
    process_events()
