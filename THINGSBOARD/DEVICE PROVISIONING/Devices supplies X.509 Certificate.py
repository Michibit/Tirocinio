# Import delle librerie necessarie
import ssl
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from paho.mqtt.client import Client
from json import dumps, loads

# Dizionario per i risultati dei codici di ritorno MQTT
RESULT_CODES = {
    1: "versione del protocollo non corretta",
    2: "identificativo del client non valido",
    3: "server non disponibile",
    4: "username o password non validi",
    5: "non autorizzato",
}

PATH_CERT = "THINGSBOARD/cert/certClient.pem"
PATH_KEY = "THINGSBOARD/cert/keyClient.pem"

# Funzione per la raccolta dei dati di configurazione da parte dell'utente


def collect_required_data():
    config = {}
    print("\n\n", "="*80, sep="")
    print(" "*10, "\033[1m\033[94mThingsBoard device provisioning with X509 certificate authorization example script. MQTT API\033[0m", sep="")
    print("="*80, "\n\n", sep="")
    # Raccolta dell'input dall'utente
    host = input(
        "Inserisci l'\033[93mhost\033[0m di ThingsBoard o lascia vuoto per usare il valore predefinito (thingsboard.cloud): ")
    config["host"] = host if host else "mqtt.thingsboard.cloud"
    port = input(
        "Inserisci la porta \033[93mSSL\033[0m di ThingsBoard o lascia vuoto per usare il valore predefinito (8883): ")
    config["port"] = int(port) if port else 8883
    config["provision_device_key"] = input(
        "Inserisci la \033[93mchiave\033[0m del dispositivo di provision: ")
    config["provision_device_secret"] = input(
        "Inserisci il \033[93msegreto\033[0m del dispositivo di provision: ")
    device_name = input(
        "Inserisci il \033[93mnome del dispositivo\033[0m o lascia vuoto per generarne uno: ")
    if device_name:
        config["device_name"] = device_name
    print("\n", "="*80, "\n", sep="")
    return config

# Funzione per generare certificati e chiavi


def generate_certs(ca_certfile="mqttserver.pub.pem"):
    # Caricamento del certificato del server CA
    root_cert = None
    try:
        with open(ca_certfile, "r") as ca_file:
            root_cert = x509.load_pem_x509_certificate(
                str.encode(ca_file.read()), default_backend())
    except Exception as e:
        print("Failed to load CA certificate: %r" % e)

    # Se il certificato del server CA è stato caricato con successo, si procede con la generazione di certificato e chiave
    if root_cert is not None:
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )
        new_subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost")
        ])
        certificate = (
            x509.CertificateBuilder()
            .subject_name(new_subject)
            .issuer_name(new_subject)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365*10))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .sign(private_key=private_key, algorithm=hashes.SHA256(), backend=default_backend())
        )

        # Salvataggio del certificato e della chiave su file
        with open("cert.pem", "wb") as cert_file:
            cert_file.write(certificate.public_bytes(
                encoding=serialization.Encoding.PEM))

        with open("key.pem", "wb") as key_file:
            key_file.write(private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                     format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                     encryption_algorithm=serialization.NoEncryption(),
                                                     ))

# Funzione per leggere certificato e chiave


def read_cert():
    cert = None
    key = None
    try:
        with open(PATH_CERT, "r") as cert_file:
            cert = cert_file.read()
        with open(PATH_KEY, "r") as key_file:
            key = key_file.read()
    except Exception as e:
        print("Cannot read certificate with error: %r" % e)
    return cert, key


# Classe per il client MQTT di provision

class ProvisionClient(Client):
    PROVISION_REQUEST_TOPIC = "/provision/request"
    PROVISION_RESPONSE_TOPIC = "/provision/response"

    def __init__(self, host, port, provision_request):
        super().__init__()
        self._host = host
        self._port = port
        self._username = "provision"
        # Impostazione della connessione TLS utilizzando il certificato del server CA
        self.tls_set(ca_certs="mqttserver.pub.pem",
                     tls_version=ssl.PROTOCOL_TLSv1_2)
        self.on_connect = self.__on_connect
        self.on_message = self.__on_message
        self.__provision_request = provision_request

    def __on_connect(self, client, userdata, flags, rc):  # Callback per la connessione
        if rc == 0:
            print("[Provisioning client] Connesso a ThingsBoard ")
            # Iscrizione al topic di risposta per la provision
            client.subscribe(self.PROVISION_RESPONSE_TOPIC)
            provision_request = dumps(self.__provision_request)
            print("[Provisioning client] Invio della richiesta di provision %s" %
                  provision_request)
            # Pubblicazione della richiesta di provision
            client.publish(self.PROVISION_REQUEST_TOPIC, provision_request)
        else:
            print("[Provisioning client] Impossibile connettersi a ThingsBoard!, risultato: %s" %
                  RESULT_CODES[rc])

    def __on_message(self, client, userdata, msg):
        decoded_payload = msg.payload.decode("UTF-8")
        print("[Provisioning client] Ricevuti dati da ThingsBoard: %s" %
              decoded_payload)
        decoded_message = loads(decoded_payload)
        provision_device_status = decoded_message.get("status")
        if provision_device_status == "SUCCESS":
            if decoded_message["credentialsValue"] == cert.replace("-----BEGIN CERTIFICATE-----\n", "")\
                                                          .replace("-----END CERTIFICATE-----\n", "")\
                                                          .replace("\n", ""):
                print(
                    "[Provisioning client] Provisioning success! Certificates are saved.")
                self.__save_credentials(cert)
            else:
                print(
                    "[Provisioning client] Returned certificate is not equal to sent one.")
        else:
            print("[Provisioning client] Provisioning was unsuccessful with status %s and message: %s" % (
                provision_device_status, decoded_message["errorMsg"]))
        self.disconnect()

    def provision(self):
        print("[Provisioning client] Connessione a ThingsBoard (provisioning client)")
        self.__clean_credentials()
        self.connect(self._host, self._port, 60)
        self.loop_forever()

    def get_new_client(self):
        client_credentials = self.__get_credentials()
        new_client = None
        if client_credentials:
            new_client = Client()
            # Impostazione della connessione TLS utilizzando il certificato e la chiave generate
            new_client.tls_set(ca_certs="mqttserver.pub.pem", certfile="cert.pem", keyfile="key.pem", cert_reqs=ssl.CERT_REQUIRED,
                               tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
            new_client.tls_insecure_set(False)
            print("[Provisioning client] Lettura delle credenziali da file.")
        else:
            print("[Provisioning client] Impossibile leggere le credenziali da file!")
        return new_client

    @staticmethod
    def __get_credentials():
        new_credentials = None
        try:
            with open("credentials", "r") as credentials_file:
                new_credentials = credentials_file.read()
        except Exception as e:
            print(e)
        return new_credentials

    @staticmethod
    def __save_credentials(credentials):
        with open("credentials", "w") as credentials_file:
            credentials_file.write(credentials)

    @staticmethod
    def __clean_credentials():
        open("credentials", "w").close()

# Callback per la connessione con le credenziali ricevute

def on_tb_connected(client, userdata, flags, rc):
    if rc == 0:
        print("[ThingsBoard client] Connesso a ThingsBoard con credenziali: username: %s, password: %s, client id: %s" % (
            client._username, client._password, client._client_id))
    else:
        print("[ThingsBoard client] Impossibile connettersi a ThingsBoard!, risultato: %s" %
              RESULT_CODES[rc])


if __name__ == '__main__':
    # Raccolta dei dati di configurazione
    config = collect_required_data()

    # Impostazioni di host e porta per ThingsBoard
    THINGSBOARD_HOST = config["host"]
    THINGSBOARD_PORT = config["port"]

    # Creazione della richiesta di provision
    PROVISION_REQUEST = {"provisionDeviceKey": config["provision_device_key"],
                         "provisionDeviceSecret": config["provision_device_secret"],
                         "credentialsType": "X509_CERTIFICATE",
                         }

    # Aggiunta del nome del dispositivo se specificato
    if config.get("device_name") is not None:
        PROVISION_REQUEST["deviceName"] = config["device_name"]

    # Generazione dei certificati e chiavi
    # Opzionale, è possibile fornire un certificato e una chiave privata
    # generate_certs()

    # Lettura dei certificati generati/forniti
    cert, key = read_cert()

    # Aggiunta dell'hash del certificato alla richiesta di provision
    # Hash = Contenuto del certificato
PROVISION_REQUEST["hash"] = cert

# Verifica se l'hash del certificato è presente nella richiesta di provision
if PROVISION_REQUEST.get("hash") is not None:
    # Creazione di un client di provision
    provision_client = ProvisionClient(
        THINGSBOARD_HOST, THINGSBOARD_PORT, PROVISION_REQUEST)
    provision_client.provision()  # Richiesta dei dati di provision
    # Ottenimento di un nuovo client con i dati di provision
    tb_client = provision_client.get_new_client()
    if tb_client:
        # Impostazione del callback per la connessione
        tb_client.on_connect = on_tb_connected
        tb_client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
        tb_client.loop_forever()  # Avvio del loop infinito
    else:
        print("Il client non è stato creato!")
else:
    print("Impossibile leggere il certificato.")
