from paho.mqtt import client as mqtt_client
from colorama import Fore, Back, Style, init
import json
import random


init(autoreset=True)
# Indrizzo del Broker utilizzato
broker = 'localhost'

# Porta in cui il broker ascolta
port = 8883

# Topic del messaggio
topic = "temperaturaTopic"


# Genero un ID - Subscriber
client_id = f'Subscriber-{random.randint(0, 1000)}'

# Credenziali di accesso
# Certificato CA del broker MQTT
cerfile = "MOSQUITTO/cert/caBuono.crt"
cerClient = "MOSQUITTO/cert/clientSub.crt"  # Certificato del Client
keyClient = "MOSQUITTO/cert/clientSub.key"  # Chiave del Client


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connessione Effettuata!\nSono in attesa di messaggi!")
        else:
            print("Non sono riuscito a connettermi, return code %d\n", rc)

    # Setto i vari campi del client
    client = mqtt_client.Client(client_id)  #  ID
    # Autenticazione  - Certificato CA - Certificato Client - Chiave Client
    client.tls_set(cerfile, cerClient, keyClient)


    #  Stabilisco connessione
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def print_json_field(key, value, key_color, value_color):
    print(f"{key_color}{key}:{Style.RESET_ALL} {value_color}{value}{Style.RESET_ALL}")


def print_colored_json(data, topic):
    print(Back.BLUE + Fore.WHITE + "Messaggio da " +
          Back.RED + Fore.WHITE + topic + Style.RESET_ALL)
    print("\n{")

    for key, value in data.items():
        print_json_field(f'"{key}"', json.dumps(
            value, indent=4), Fore.GREEN, Fore.YELLOW)

    print("\n")




def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        decoded_message = str(msg.payload.decode("utf-8"))
        print_colored_json(json.loads(decoded_message), msg.topic)

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    # Loop eterno
    client.loop_forever()


if __name__ == '__main__':
    run()
