# Introduzione

I seguenti script sono stati sviluppati come parte del mio tirocinio presso System Management S.p.A nell'ambito del protocollo MQTT.

# MOSQUITTO Scripts

Questa cartella contiene script Python che implementano varie configurazioni di client MQTT e subscriber MQTT con l'ausilio del broker MOSQUITTO (per l'installazione segui questa [guida](https://github.com/sukesh-ak/setup-mosquitto-with-docker)).
Gli script consentono di inviare messaggi contenenti la temperatura relativa a una stanza di una casa e di visualizzarli sulla console. Ogni script si differenzia per i **metodi di autenticazione** utilizzati.


![mqtt-publish-subscribe](https://github.com/Michibit/Tirocinio/assets/16355437/1bf45179-762a-4e2c-bfce-c97ba5b59225)



## Configurazioni Disponibili

### MQTT Client & Subscriber Basic

Questi script implementano un client e un subscriber MQTT, eseguendo l'autenticazione con **USERNAME - PASSWORD**.

### MQTT Client & Subscriber Intermediate

Questi script implementano un client e un subscriber MQTT, eseguendo l'autenticazione con **USERNAME - PASSWORD + CERTIFICATO CA**, quindi abilitando il protocollo TLS/SSL.

### MQTT Client & Subscriber Advanced

Questi script implementano un client e un subscriber MQTT, eseguendo l'autenticazione con **CERTIFICATO CA + CERTIFICATO CLIENT + CHIAVE CLIENT**, quindi abilitando il protocollo TLS/SSL e esegurndo la Mutua Autenticazione.

## Istruzioni per l'Utilizzo

Ciascuno degli script può essere eseguito indipendentemente. Tuttavia, prima di utilizzarli, assicurati di installare le dipendenze necessarie, inclusi un broker MOSQUITTO e il modulo `paho-mqtt` (se necessario):

```bash
pip install paho-mqtt

