# Introduzione

Gli script seguenti sono stati sviluppati durante il mio tirocinio presso System Management S.p.A.

# Cartella MOSQUITTO

Questa cartella contiene script Python che implementano diverse configurazioni di client MQTT e subscriber MQTT tramite il broker MOSQUITTO. Per installare il broker, segui questa [guida](https://github.com/sukesh-ak/setup-mosquitto-with-docker). Gli script permettono l'invio di messaggi contenenti la temperatura di una stanza, visualizzabili sulla console. Ciascuno di essi si distingue per i **metodi di autenticazione** utilizzati.

# Cartella THINGSBOARD

Questa cartella contiene script Python che implementano diverse configurazioni di client MQTT con l'ausilio di THINGSBOARD. Gli script consentono l'invio di un payload JSON contenente informazioni come il nome del dispositivo, il tipo, il modello e le varie telemetrie. Ogni script presenta differenze nei **metodi di autenticazione** utilizzati.

## Sottocartella DEVICE PROVISIONING

All'interno di questa sottocartella, troverai script Python che implementano diverse strategie di provisioning per THINGSBOARD. Ciascuno di essi richiede parametri specifici per essere eseguito correttamente.

## Sottocartella PROVISION BULK

Questa sottocartella contiene file CSV di esempio per eseguire il Provision Bulk all'interno di Thingsboard.

# NOTE

Le cartelle "cert" contengono certificati generati con Open SSL per effettuare i test necessari. Tuttavia, normalmente è consigliato utilizzare certificati validati da un'Authority.