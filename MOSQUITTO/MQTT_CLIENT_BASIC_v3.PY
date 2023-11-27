import csv
import io
import random
import time
import paho.mqtt.client as mqtt


# Configurazione del broker
MQTT_BROKER_HOST = "127.0.0.1"
MQTT_BROKER_PORT = 1886
MQTT_TOPIC = "/converter/data"

#  Credenziali Broker
USERNAME = "user1"
PASSWORD = "michi"


def on_connect(client, userdata, flags, rc):
    print("Connesso al broker con codice di risultato " + str(rc))


# Creazione di un client
client = mqtt.Client()

# Impostazione delle funzioni di callback
client.on_connect = on_connect

# Connessione al broker MQTT
client.username_pw_set(USERNAME, PASSWORD)
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, 60)

while True:
    temperature = random.randint(10, 30)
    humidity = random.randint(40, 60)

    # Messaggio da pubblicare
    payload = {
        "serialNumber": "SN-002",
        "sensorType": "Thermometer",
        "sensorModel": "T1000",
        "temp": temperature,
        "hum": humidity
    }
    # Utilizza io.StringIO per memorizzare temporaneamente i dati CSV in una stringa
    csv_output = io.StringIO()

    # Utilizza csv.writer per scrivere i dati del payload nella stringa CSV
    csv_writer = csv.writer(csv_output)

    csv_writer.writerow(['serialNumber', 'sensorType',
                        'sensorModel', 'temp', 'hum'])
    csv_writer.writerow([payload['serialNumber'], payload['sensorType'],
                        payload['sensorModel'], payload['temp'], payload['hum']])

    # Ottieni la stringa CSV
    csv_string = csv_output.getvalue()

    # Chiudi io.StringIO
    csv_output.close()

    client.publish(MQTT_TOPIC, csv_string, qos=1)

    print(f"Dati inviati: {csv_string}")
    time.sleep(5)
