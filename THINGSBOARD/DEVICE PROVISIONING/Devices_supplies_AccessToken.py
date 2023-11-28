from paho.mqtt.client import Client
from json import dumps, loads

# Definizione dei codici di risultato per la connessione MQTT
RESULT_CODES = {
    1: "versione di protocollo non corretta",
    2: "identificatore del client non valido",
    3: "server non disponibile",
    4: "username o password non valide",
    5: "non autorizzato",
}

# Nome del file che conterrà le credenziali fornite dal dispositivo
FILE_CREDENTIALS = "credentialsSuppliedByDevice"

# Funzione per raccogliere i dati richiesti dall'utente
def collect_required_data():
    config = {}
    print("\n\n", "="*80, sep="")
    print(" "*10, "\033[1m\033[94mEsempio di script per la configurazione di dispositivi ThingsBoard con autorizzazione tramite token di accesso. API MQTT\033[0m", sep="")
    print("="*80, "\n\n", sep="")
    host = input(
        "Per favore scrivi il tuo \033[93mhost ThingsBoard\033[0m o lascialo vuoto per usare quello predefinito (thingsboard.cloud): ")
    config["host"] = host if host else "mqtt.thingsboard.cloud"
    port = input(
        "Per favore scrivi la tua \033[93mporta ThingsBoard\033[0m o lasciala vuota per usare quella predefinita (1883): ")
    config["port"] = int(port) if port else 1883
    config["provision_device_key"] = input(
        "Per favore scrivi la tua \033[93mchiave di provisioning del dispositivo\033[0m: ")
    config["provision_device_secret"] = input(
        "Per favore scrivi il tuo \033[93msegreto di provisioning del dispositivo\033[0m: ")
    config["token"] = input(
        "Per favore scrivi il \033[93mtoken di accesso del dispositivo\033[0m: ")
    device_name = input(
        "Per favore scrivi il \033[93mnome del dispositivo\033[0m o lascialo vuoto per generarlo: ")
    if device_name:
        config["device_name"] = device_name
    print("\n", "="*80, "\n", sep="")
    return config

# Classe per il client MQTT di provisioning


class ProvisionClient(Client):
    PROVISION_REQUEST_TOPIC = "/provision/request"
    PROVISION_RESPONSE_TOPIC = "/provision/response"

    def __init__(self, host, port, provision_request):
        super().__init__()
        self._host = host
        self._port = port
        self._username = "provision"
        self.on_connect = self.__on_connect
        self.on_message = self.__on_message
        self.__provision_request = provision_request

    def __on_connect(self, client, userdata, flags, rc):  # Callback per la connessione
        if rc == 0:
            print("[Client di provisioning] Connesso a ThingsBoard ")
            # Iscrizione al topic di risposta del provisioning
            client.subscribe(self.PROVISION_RESPONSE_TOPIC)
            provision_request = dumps(self.__provision_request)
            print("[Client di provisioning] Invio della richiesta di provisioning %s" %
                  provision_request)
            # Pubblicazione sul topic di richiesta di provisioning
            client.publish(self.PROVISION_REQUEST_TOPIC, provision_request)
        else:
            print("[Client di provisioning] Impossibile connettersi a ThingsBoard!, risultato: %s" %
                  RESULT_CODES[rc])

    def __on_message(self, client, userdata, msg):
        decoded_payload = msg.payload.decode("UTF-8")
        print("[Client di provisioning] Ricevuti dati da ThingsBoard: %s" %
              decoded_payload)
        decoded_message = loads(decoded_payload)
        provision_device_status = decoded_message.get("status")
        if provision_device_status == "SUCCESS":
            self.__save_credentials(decoded_message["credentialsValue"])
        else:
            print("[Client di provisioning] Il provisioning non è riuscito con stato %s e messaggio: %s" % (
                provision_device_status, decoded_message["errorMsg"]))
        self.disconnect()

    def provision(self):
        print(
            "[Client di provisioning] Connessione a ThingsBoard (client di provisioning)")
        self.__clean_credentials()
        self.connect(self._host, self._port, 60)
        self.loop_forever()

    def get_new_client(self):
        client_credentials = self.__get_credentials()
        new_client = None
        if client_credentials:
            new_client = Client()
            new_client.username_pw_set(client_credentials)
            print("[Client di provisioning] Lettura delle credenziali dal file.")
        else:
            print(
                "[Client di provisioning] Impossibile leggere le credenziali dal file!")
        return new_client

    @staticmethod
    def __get_credentials():
        new_credentials = None
        try:
            with open(FILE_CREDENTIALS, "r") as credentials_file:
                new_credentials = credentials_file.read()
        except Exception as e:
            print(e)
        return new_credentials

    @staticmethod
    def __save_credentials(credentials):
        with open(FILE_CREDENTIALS, "w") as credentials_file:
            credentials_file.write(credentials)

    @staticmethod
    def __clean_credentials():
        open(FILE_CREDENTIALS, "w").close()

# Callback per la connessione con le credenziali ricevute


def on_tb_connected(client, userdata, flags, rc):
    if rc == 0:
        print("[Client ThingsBoard] Connesso a ThingsBoard con le credenziali: %s" %
              client._username.decode())
    else:
        print("[Client ThingsBoard] Impossibile connettersi a ThingsBoard!, risultato: %s" %
              RESULT_CODES[rc])


# Parte principale del programma
if __name__ == '__main__':

    config = collect_required_data()

    THINGSBOARD_HOST = config["host"]  # Host dell'istanza ThingsBoard
    THINGSBOARD_PORT = config["port"]  # Porta MQTT dell'istanza ThingsBoard

    PROVISION_REQUEST = {"provisionDeviceKey": config["provision_device_key"],  # Chiave di provisioning del dispositivo, sostituire con il valore dal profilo del dispositivo.
                         # Segreto di provisioning del dispositivo, sostituire con il valore dal profilo del dispositivo.
                         "provisionDeviceSecret": config["provision_device_secret"],
                         "credentialsType": "ACCESS_TOKEN",
                         "token": config["token"],
                         }
    if config.get("device_name") is not None:
        PROVISION_REQUEST["deviceName"] = config["device_name"]
    provision_client = ProvisionClient(
        THINGSBOARD_HOST, THINGSBOARD_PORT, PROVISION_REQUEST)

    # Richiesta dei dati provisionati
    provision_client.provision()

    # Ottenimento del client con i dati provisionati
    tb_client = provision_client.get_new_client()
    if tb_client:
        # Impostazione della callback per la connessione
        tb_client.on_connect = on_tb_connected
        tb_client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
        tb_client.loop_forever()  # Avvio del loop infinito
    else:
        print("Il client non è stato creato!")
