import paho.mqtt.client as mqtt
import random
import time
import json


broker_address = "localhost"  # Indirizzo IP o nome host del broker
port = 8883  # Porta di default per MQTT che supporta TLS/SSL
topic = "temperaturaTopic"

# Credenziali di accesso
username = 'admin2'
password = 'admin@123'


# Certificato CA del broker MQTT
cerfile = "MOSQUITTO/cert/caBuono.crt"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connessione al broker MQTT riuscita")
    else:
        print(f"Connessione al broker MQTT fallita, codice di ritorno: {rc}")


def publish(client):
    #  Inizializzo variabili
    stanze = ["Salone", "Stanza da letto", "Soggiorno", "Bagno"]
    temperature = random.randint(0, 50)

    while True:

        # Estrai casualmente una stanza dalla lista
        random.shuffle(stanze)
        time.sleep(1)
        nome_stanza = stanze[0]

        # Creazione del messaggio
        data = {
            "ts": int(round(time.time() * 1000)),
            "values": {
                "name": nome_stanza,
                "temperature": temperature
            }
        }

        # Conversione in Json
        json_string = json.dumps(data, indent=2)

        # Pubblicazione del messaggio
        result = client.publish(topic, json_string, qos=1)

        #  Verifica se il messaggio è stato inviato
        status = result[0]
        if status == 0:
            print(
                f"Inviato correttamente al topic: {topic} n: {str(result[1])}")
        else:
            print(f"Impossibile inviare il msg al topic: {topic}")


# Crea un client MQTT
client = mqtt.Client()

# Autenticazione - Username e Password - Certificato
client.tls_set(cerfile)
client.username_pw_set(username, password)

# Imposta la funzione di callback per la connessione
client.on_connect = on_connect

# Connessione al broker MQTT
client.connect(broker_address, port)

# Avvio del loop del client MQTT
client.loop_start()

publish(client)

# Disconnessione dal broker MQTT
client.disconnect()
client.loop_stop()
