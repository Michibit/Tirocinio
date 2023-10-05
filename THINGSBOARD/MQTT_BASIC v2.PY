import paho.mqtt.client as mqtt
import random
import json
import time

# Definizione dei parametri di connessione
THINGSBOARD_HOST = "localhost"
CLIENT_ID = "fv1gt9eha82192gxe9rl"
USERNAME = "54gshi3cap1eahnb0zeu"
PASSWORD = "g90tai35objlkj7jys07"

TOPIC = "v1/devices/me/telemetry"
PORT = 1883


# Funzione di callback quando la connessione al broker MQTT è stabilita
def on_connect(client, userdata, flags, rc):
    print("Connesso con codice di stato: " + str(rc))

# Funzione per pubblicare dati
def publish_data():
    client = mqtt.Client(CLIENT_ID)

    # Imposta la funzione di callback
    client.on_connect = on_connect

    # Imposta l'username e la password per la connessione MQTT
    client.username_pw_set(username=USERNAME, password=PASSWORD)

    # Connettiti a ThingsBoard
    client.connect(THINGSBOARD_HOST, PORT)
    stanze = ["Salone", "Stanza da letto", "Soggiorno", "Bagno"]

    while True:
        # Generazione dati casuali per la simulazione
        temperature = random.uniform(20, 40)
        random.shuffle(stanze)
        nome_stanza = stanze[0]


        # Crea un payload JSON con i dati da inviare 
        payload = {
            "ts": int(round(time.time() * 1000)),
            "values": {
                "name": nome_stanza,
                "temperature": temperature
            }
        }

        # Pubblica il payload su ThingsBoard
        client.publish(TOPIC, json.dumps(payload))

        print(f"Dati inviati: {payload}")

        # Attendi 5 secondi prima di inviare il prossimo set di dati
        time.sleep(5)

# Avvia la pubblicazione dei dati
publish_data()
