import paho.mqtt.client as mqtt
import random
import time
import json


broker_address = "localhost"  # Indirizzo IP o nome host del broker MQTT
port = 9001  # Porta di default per MQTT con supporto TLS/SSL
topic = "/sensor/data/1"

# Credenziali di accesso

cerfile = "MOSQUITTO/cert/ca.crt"  # Certificato CA del broker MQTT
cerClient = "MOSQUITTO/cert/client.crt"  # Certificato del Client
keyClient = "MOSQUITTO/cert/client.key"  # Chiave privata del client


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connessione al broker MQTT riuscita")
    else:
        print(f"Connessione al broker MQTT fallita, codice di ritorno: {rc}")


def publish(client):
    #  Inizializzo variabili
    stanze = ["Salone", "Stanza da letto", "Soggiorno", "Bagno"]
    temperature = random.randint(0, 50)

    msg_count = 1
    while True:

        # Estrai casualmente una stanza dalla lista
        random.shuffle(stanze)
        time.sleep(1)
        temperature = random.randint(0, 50)
        humidity = random.randint(10, 60)

        # Messaggio da pubblicare
        payload = {
        "serialNumber": "SN-002",
        "sensorType": "Thermometer",
        "sensorModel": "T1000",
        "temp": temperature,
        "hum": humidity
        }

        # Conversione in Json
        json_string = json.dumps(payload, indent=2)

        # Pubblicazione del messaggio
        result = client.publish(topic, json_string, qos=2)

        #  Verifica se il messaggio è stato inviato
        status = result[0]
        if status == 0:
            print(
                f"Inviato correttamente al topic: {topic} n: {str(result[1])}")
        else:
            print(f"Impossibile inviare il msg al topic: {topic}")


# Crea un client MQTT
client = mqtt.Client()

# AUTENTICAZIONE - Certificato CA - Certificato client - Chiave client
client.tls_set(cerfile, cerClient, keyClient)


client.on_connect = on_connect

# Connessione al broker MQTT
client.connect(broker_address, port)

# Avvio del loop del client MQTT
client.loop_start()

publish(client)

# Disconnessione dal broker MQTT
client.disconnect()
client.loop_stop()
