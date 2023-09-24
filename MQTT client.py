import random
import time
import json
from paho.mqtt import client as mqtt_client

# Broker utilizzato
broker = 'localhost'

# Porta in cui il broker ascolta
port = 1883

# Topic del messaggio
topic = "temperaturaTopic"


# Genero un ID - Client
client_id = f'Publisher-{random.randint(0, 1000)}'

# Credenziali di accesso
username = 'michi'
password = 'michi'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connessione Effettuata!")
        else:
            print("Non sono riuscito a connettermi, return code %d\n", rc)

    # Setto i vari campi del client
    client = mqtt_client.Client(client_id)  #  ID
    # Autenticazione - Username e Password -
    client.username_pw_set(username, password)

    #  Stabilisco connessione
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    #  Inizializzo variabili
    stanze = ["Salone", "Stanza da letto", "Soggiorno", "Bagno"]
    temperature = random.randint(0, 50)

    msg_count = 1
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
        result = client.publish(topic, json_string, qos = 2)

        #  Verifica se il messaggio è stato inviato
        status = result[0]
        if status == 0:
            print(f"Inviato correttamente al topic: {topic}")
        else:
            print(f"Impossibile inviare il msg al topic: {topic}")
        msg_count += 1

        #  Ogni 5 iterazioni cambio i parametri
    


def run():
    client = connect_mqtt()
    
    # Apro connessione 
    client.loop_start()

    publish(client)

    # Chiudo connessione
    client.loop_stop()


if __name__ == '__main__':
    run()
