import paho.mqtt.client as mqtt
import time
import random
import json

# Definisci i parametri di connessione al broker 
HOST = "localhost"  # Indirizzo del broker 
PORT = 8883  # Porta del broker 
TOPIC = "v1/devices/me/telemetry"  # Argomento (topic) 

# Percorsi ai file dei certificati e delle chiavi
CAFILE = "THINGSBOARD/cert/server.pub.pem"
CERTFILE = "THINGSBOARD/cert/certClient.pem"
KEYFILE = "THINGSBOARD/cert/keyClient.pem"

# Messaggio JSON da pubblicare
payload = '{"temperature": 25}'

# Funzione di callback quando la connessione al broker MQTT è stabilita
def on_connect(client, userdata, flags, rc):
    print("Connesso con codice di stato: " + str(rc))

# Crea un client MQTT
client = mqtt.Client()

# Imposta la funzione di callback per la connessione
client.on_connect = on_connect

# Imposta i certificati e le chiavi per la connessione sicura
client.tls_set(CAFILE, CERTFILE, KEYFILE)

# Connettiti al broker MQTT
client.connect(HOST, PORT)

# Avvia il loop di rete per gestire le comunicazioni con il broker


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
