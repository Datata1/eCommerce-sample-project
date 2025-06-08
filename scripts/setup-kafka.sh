#!/bin/bash

set -e # Beendet das Skript sofort, wenn ein Befehl fehlschlägt

# --- Konfiguration ---
CERTS_DIR="./certs"
PASSWORD="meinPasswort" 
HOSTNAME="ws-server-67705-kafka.workspaces"

KEYSTORE_FILE="${CERTS_DIR}/kafka.server.keystore.jks"
TRUSTSTORE_FILE="${CERTS_DIR}/kafka.client.truststore.jks"

echo "download kafka"
[ -f ./kafka_2.13-4.0.0.tgz ] || wget https://dlcdn.apache.org/kafka/4.0.0/kafka_2.13-4.0.0.tgz

echo "unzip tar archive"
[ -d ./services/kafka_2.13-4.0.0 ] || tar -xzf kafka_2.13-4.0.0.tgz -C ./services/

echo "Kafka-Speicher initialisieren (falls nötig)..."

# Definiere den persistenten Speicherort
LOG_DIR="/home/user/app/.codesphere-internal/kafka-logs"

# Erstelle das Verzeichnis, falls es nicht existiert
mkdir -p "$LOG_DIR"

if [ ! -f "$LOG_DIR/meta.properties" ]; then
    echo "Formatiere neuen Kafka-Speicher..."
    
    (
        cd services/kafka_2.13-4.0.0 && \
        UUID=$(bin/kafka-storage.sh random-uuid) && \
        bin/kafka-storage.sh format -t "$UUID" -c config/server.properties --standalone
    )
    
    echo "Formatierung abgeschlossen."
else
    echo "Kafka-Speicher bereits vorhanden. Überspringe Formatierung."
fi
# --- Hauptlogik ---

mkdir -p "$CERTS_DIR"

if [ -f "$KEYSTORE_FILE" ]; then
    echo "Keystore '$KEYSTORE_FILE' existiert bereits. Überspringe Zertifikatserstellung."
    exit 0
fi

echo "Keystore nicht gefunden. Starte den Prozess zur Zertifikatserstellung..."

CA_KEY="${CERTS_DIR}/ca-key"
CA_CERT="${CERTS_DIR}/ca-cert"
CSR_FILE="${CERTS_DIR}/cert-file"
SIGNED_CERT_FILE="${CERTS_DIR}/cert-signed"

echo "--> Erstelle Certificate Authority (CA)..."
openssl req -new -newkey rsa:4096 -days 3650 -x509 \
  -subj "/CN=Kafka-Self-Signed-CA" \
  -keyout "$CA_KEY" -out "$CA_CERT" -nodes

echo "--> Erstelle Server-Keystore und Certificate Signing Request (CSR)..."
keytool -genkeypair -keystore "$KEYSTORE_FILE" -alias localhost -keyalg RSA -keysize 4096 -validity 3650 \
  -dname "CN=${HOSTNAME}" \
  -storepass "$PASSWORD" -keypass "$PASSWORD"

keytool -keystore "$KEYSTORE_FILE" -alias localhost -certreq -file "$CSR_FILE" -storepass "$PASSWORD"

echo "--> Signiere Server-Zertifikat mit CA..."
openssl x509 -req -CA "$CA_CERT" -CAkey "$CA_KEY" -in "$CSR_FILE" -out "$SIGNED_CERT_FILE" -days 3650 -CAcreateserial

echo "--> Importiere CA-Zertifikat und signiertes Server-Zertifikat in den Keystore..."
keytool -keystore "$KEYSTORE_FILE" -alias CARoot -import -file "$CA_CERT" -storepass "$PASSWORD" -noprompt
keytool -keystore "$KEYSTORE_FILE" -alias localhost -import -file "$SIGNED_CERT_FILE" -storepass "$PASSWORD"

echo "--> Erstelle Client-Truststore..."
keytool -keystore "$TRUSTSTORE_FILE" -alias CARoot -import -file "$CA_CERT" -storepass "$PASSWORD" -noprompt

echo "--> Räume temporäre Dateien auf..."
rm -f "$CSR_FILE" "$SIGNED_CERT_FILE" "${CERTS_DIR}/ca-key.srl"

echo "Zertifikatserstellung erfolgreich abgeschlossen!"

echo "copy server setting"
cp kafka-config/server.properties services/kafka_2.13-4.0.0/config/server.properties