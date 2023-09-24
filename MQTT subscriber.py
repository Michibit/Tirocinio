from paho.mqtt import client as mqtt_client
import json
import random

# Indrizzo del Broker utilizzato
broker = 'localhost'

# Porta in cui il broker ascolta
port = 8883

# Topic del messaggio
topic = "temperaturaTopic"


# Genero un ID - Subscriber
client_id = f'Subscriber-{random.randint(0, 1000)}'

# Credenziali di accesso
username = 'michi'
password = 'michi'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connessione Effettuata!\nSono in attesa di messaggi!")
        else:
            print("Non sono riuscito a connettermi, return code %d\n", rc)

    # Setto i vari campi del client
    client = mqtt_client.Client(client_id)  #  ID
    # Autenticazione - Username e Password - Certificato
    client.tls_set("caBuono.crt")
    client.username_pw_set(username, password)

    #  Stabilisco connessione
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        decoded_message = str(msg.payload.decode("utf-8"))
    
        print(f"Ho ricevuto:\n `{json.loads(decoded_message)}`\n dal topic: `{msg.topic}`\n\n")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    # Loop eterno
    client.loop_forever()


if __name__ == '__main__':
    run()
