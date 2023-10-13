import paho.mqtt.client as mqtt
import json
import random
import time

# Definisci i parametri di connessione a ThingsBoard
THINGSBOARD_HOST = "localhost"
ACCESS_TOKEN = "fmc1as5uzyrli0wt0tms"

TOPIC = "v1/devices/me/telemetry"
PORT = 8883

# Funzione di callback quando la connessione al broker MQTT è stabilita
def on_connect(client, userdata, flags, rc):
    print("Connesso con codice di stato: " + str(rc))

# Funzione per pubblicare dati casuali su ThingsBoard
def publish_data():
    client = mqtt.Client()

    # Imposta la funzione di callback
    client.on_connect = on_connect

    # Connettiti a ThingsBoard con l'access token
    client.tls_set("THINGSBOARD/cert/server.pub.pem")
    client.username_pw_set(ACCESS_TOKEN)
    client.connect(THINGSBOARD_HOST, PORT)

    while True:
        # Genera dati casuali per la simulazione
        temperature = random.uniform(10, 90)
        humidity = random.uniform(40, 60)

        # Crea un payload JSON con i dati da inviare a ThingsBoard
        payload = {
            "temperature": temperature,
            "humidity": humidity
        }

        # Pubblica il payload su ThingsBoard
        client.publish(TOPIC, json.dumps(payload), qos=1)

        print(f"Dati inviati: {payload}")

        # Attendi 5 secondi prima di inviare il prossimo set di dati
        time.sleep(5)

# Avvia la pubblicazione dei dati
publish_data()
