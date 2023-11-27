from paho.mqtt.client import Client
from json import dumps, loads

# Dizionario per associare i codici di risultato della connessione a messaggi più descrittivi
RESULT_CODES = {
    1: "incorrect protocol version",
    2: "invalid client identifier",
    3: "server unavailable",
    4: "bad username or password",
    5: "not authorised",
}

def collect_required_data():
    # Funzione per raccogliere i dati di configurazione dal'utente
    config = {}
    print("\n\n", "="*80, sep="")
    print(" "*10, "\033[1m\033[94mThingsBoard device provisioning with basic authorization example script.\033[0m", sep="")
    print("="*80, "\n\n", sep="")
    host = input("Please write your ThingsBoard \033[93mhost\033[0m or leave it blank to use default (thingsboard.cloud): ")
    config["host"] = host if host else "mqtt.thingsboard.cloud"
    port = input("Please write your ThingsBoard \033[93mport\033[0m or leave it blank to use default (1883): ")
    config["port"] = int(port) if port else 1883
    config["provision_device_key"] = input("Please write \033[93mprovision device key\033[0m: ")
    config["provision_device_secret"] = input("Please write \033[93mprovision device secret\033[0m: ")
    device_name = input("Please write \033[93mdevice name\033[0m or leave it blank to generate: ")
    if device_name:
        config["device_name"] = device_name
    print("\n", "="*80, "\n", sep="")
    return config


class ProvisionClient(Client):
    # Sottoclasse di Client per gestire la registrazione del dispositivo su ThingsBoard

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
            print("[Provisioning client] Connected to ThingsBoard ")
            client.subscribe(self.PROVISION_RESPONSE_TOPIC)  # Iscrizione al topic di risposta del provisioning
            provision_request = dumps(self.__provision_request)
            print("[Provisioning client] Sending provisioning request %s" % provision_request)
            client.publish(self.PROVISION_REQUEST_TOPIC, provision_request)  # Invio della richiesta di provisioning
        else:
            print("[Provisioning client] Cannot connect to ThingsBoard!, result: %s" % RESULT_CODES[rc])

    def __on_message(self, client, userdata, msg):
        # Callback per la ricezione di un messaggio
        decoded_payload = msg.payload.decode("UTF-8")
        print("[Provisioning client] Received data from ThingsBoard: %s" % decoded_payload)
        decoded_message = loads(decoded_payload)
        provision_device_status = decoded_message.get("status")
        if provision_device_status == "SUCCESS":
            self.__save_credentials(decoded_message["credentialsValue"])
        else:
            print("[Provisioning client] Provisioning was unsuccessful with status %s and message: %s" % (provision_device_status, decoded_message["errorMsg"]))
        self.disconnect()

    def provision(self):
        # Metodo per gestire la connessione e la richiesta di provisioning
        print("[Provisioning client] Connecting to ThingsBoard (provisioning client)")
        self.__clean_credentials()
        self.connect(self._host, self._port, 60)
        self.loop_forever()

    def get_new_client(self):
        # Metodo per ottenere un nuovo client configurato con le credenziali di registrazione
        client_credentials = self.__get_credentials()
        new_client = None
        if client_credentials:
            new_client = Client()
            new_client.username_pw_set(client_credentials)
            print("[Provisioning client] Read credentials from file.")
        else:
            print("[Provisioning client] Cannot read credentials from file!")
        return new_client

    @staticmethod
    def __get_credentials():
        # Metodo statico per ottenere le credenziali dal file
        new_credentials = None
        try:
            with open("credentials", "r") as credentials_file:
                new_credentials = credentials_file.read()
        except Exception as e:
            print(e)
        return new_credentials

    @staticmethod
    def __save_credentials(credentials):
        # Metodo statico per salvare le credenziali su un file
        with open("credentials", "w") as credentials_file:
            credentials_file.write(credentials)

    @staticmethod
    def __clean_credentials():
        # Metodo statico per cancellare le credenziali salvate
        open("credentials", "w").close()


def on_tb_connected(client, userdata, flags, rc):  # Callback per la connessione al servizio ThingsBoard
    if rc == 0:
        print("[ThingsBoard client] Connected to ThingsBoard with credentials: %s" % client._username.decode())
    else:
        print("[ThingsBoard client] Cannot connect to ThingsBoard!, result: %s" % RESULT_CODES[rc])




# Blocco principale del codice
if __name__ == '__main__':

    # Raccoglie i dati di configurazione
    config = collect_required_data()
    
    # Configurazione dell'host e della porta di ThingsBoard
    THINGSBOARD_HOST = config["host"]
    THINGSBOARD_PORT = config["port"]

    # Creazione della richiesta di provisioning
    PROVISION_REQUEST = {"provisionDeviceKey": config["provision_device_key"],
                         "provisionDeviceSecret": config["provision_device_secret"],
                         }

    # Aggiunge il nome del dispositivo alla richiesta, se fornito
    if config.get("device_name") is not None:
        PROVISION_REQUEST["deviceName"] = config["device_name"]

    # Creazione e avvio del client di provisioning
    provision_client = ProvisionClient(THINGSBOARD_HOST, THINGSBOARD_PORT, PROVISION_REQUEST)
    provision_client.provision()

    # Ottenimento di un nuovo client con le credenziali appena registrate
    tb_client = provision_client.get_new_client()

    # Connessione del nuovo client a ThingsBoard
    if tb_client:
        tb_client.on_connect = on_tb_connected
        tb_client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
        tb_client.loop_forever()
    else:
        print("Client was not created!")
