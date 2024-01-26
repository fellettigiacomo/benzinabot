import dbHandler
import datetime
import requests
import csv

url_prezzoalle8= "https://www.mimit.gov.it/images/exportCSV/prezzo_alle_8.csv"
url_anagrafica= "https://www.mimit.gov.it/images/exportCSV/anagrafica_impianti_attivi.csv"

# init mysql
mysql = dbHandler.ch("localhost", "root", "", "benzinabot");

class dataHandler:
    def download_and_insert_data(self):
        # controlla se i dati sono già stati scaricati oggi
        print("DEBUG: controllo se i dati sono aggiornati")
        fileUrl = "latestDbUpdate.txt"
        file = open(fileUrl, "r")
        latestDbUpdate = file.read()
        file.close()
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        if latestDbUpdate == today:
            print("DEBUG: dati aggiornati, non è necessario scaricarli")
            return
        print("DEBUG: dati non aggiornati, cancellazione tabelle")
        mysql.truncate("prezzi")
        mysql.truncate("anagrafica")
        print("DEBUG: download avviato")
        # download di prezzo_alle_8.csv
        response_prezzoalle8 = requests.get(url_prezzoalle8)
        prezzoalle8_data = response_prezzoalle8.content.decode('utf-8').splitlines()

        # download di anagrafica_impianti_attivi.csv
        response_anagrafica = requests.get(url_anagrafica)
        anagrafica_data = response_anagrafica.content.decode('utf-8').splitlines()

        print("DEBUG: inserimento dati nella tabella prezzi")
        # inserisci dati in prezzi
        for row in csv.reader(prezzoalle8_data[2:], delimiter=';'): 
            idImpianto = int(row[0])
            descCarburante = row[1]
            prezzo = float(row[2])
            isSelf = row[3]
            if len(isSelf) != 1:
                isSelf = "0"
            else:
                isSelf = bool(isSelf)
            dtComu =  datetime.datetime.strptime(row[4], "%d/%m/%Y %H:%M:%S")
            query = f"INSERT INTO prezzi (idImpianto, descCarburante, prezzo, isSelf, dtComu) VALUES ({idImpianto}, '{descCarburante}', {prezzo}, {isSelf}, '{dtComu}')"
            mysql.execute(query)
        
        print("DEBUG: inserimento dati nella tabella anagrafica")            
        # inserisci dati in anagrafica
        for row in csv.reader(anagrafica_data[2:], delimiter=';'):
            if len(row) != 10:
                continue
            idImpianto = int(row[0])
            
            Gestore = row[1].replace("'", "")
            Bandiera = row[2]
            TipoImpianto = row[3]
            NomeImpianto = row[4].replace("'", "")
            Indirizzo = row[5].replace("'", "")
            Comune = row[6].replace("'", "")
            Provincia = row[7]
            if len(Provincia) != 2:
                Provincia = "00"
            if row[9] == "" or row[9] == "" or row[9] == "NULL" or row[9] == "NULL": 
                continue
            else:
                Latitudine = float(row[8])
                Longitudine = float(row[9])

            query = f"INSERT INTO anagrafica (idImpianto, Gestore, Bandiera, TipoImpianto, NomeImpianto, Indirizzo, Comune, Provincia, Latitudine, Longitudine) VALUES ({idImpianto}, '{Gestore}', '{Bandiera}', '{TipoImpianto}', '{NomeImpianto}', '{Indirizzo}', '{Comune}', '{Provincia}', {Latitudine}, {Longitudine})"
            mysql.execute(query)
            
        print("DEBUG: download e inserimento dati completato")
        # aggiorna latestDbUpdate
        file = open(fileUrl, "w")
        file.write(today)
        file.close()
        mysql.close()

    def __init__(self):
        self.download_and_insert_data()
