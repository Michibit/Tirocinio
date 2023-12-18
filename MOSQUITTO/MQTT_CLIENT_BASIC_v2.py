import json
import random
import time
import paho.mqtt.client as mqtt

# Configurazione del broker
MQTT_BROKER_HOST = "192.168.1.60"
MQTT_BROKER_PORT = 1886
MQTT_TOPIC = "/sensor/data/1"

#  Credenziali Broker
USERNAME = "user1"
PASSWORD = "michi"


# Funzione di callback chiamata quando il client si è connesso al broker
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
    temperature = random.randint(0, 50)
    humidity = random.randint(10, 60)

    # Messaggio da pubblicare
    payload = {
        "serialNumber": "SN-001",
        "sensorType": "Thermometer",
        "sensorModel": "T1000",
        "temp": temperature,
        "hum": humidity
    }

    client.publish(MQTT_TOPIC, json.dumps(payload))

    print(f"Dati inviati: {payload}")
    time.sleep(1)
