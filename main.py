import requestHandler
import dbHandler
import dataHandler
import humanHandler
import time

# init bot 
bot = requestHandler.rh()
dataHandler = dataHandler.dataHandler()
humanHandler = humanHandler.humanHandler()
mysql = dbHandler.ch("localhost", "root", "", "benzinabot");
lastUpdateId = None

# bot in funzione
while True:
    updates = bot.getUpdates(lastUpdateId)
    if updates['ok'] == False:
        print("errore telegram -> " + updates['description'])
    else:
        updates = updates['result']
        # se il messaggio non è vuoto
        if len(updates) > 0:
            # controllo se nel messaggio c'è il campo text che vuol dire che il mesaggio è un testo e non una posizione o un'immagine
            if 'text' in updates[-1]['message']:
                text = updates[-1]['message']['text']
                chat_id = updates[-1]['message']['chat']['id']
                user_id = updates[-1]['message']['from']['id']
                lastUpdateId = updates[-1]['update_id'] + 1
                # avvio del bot
                if text == '/start':
                    # prima volta dell'utente che non è presente nel database
                    if mysql.checkUser(user_id) == False:
                        #chiedo le informazioni base dell'utente per salvarlo nel database
                        bot.sendMessage(chat_id, "Benvenuto su Benzinabot! \n\nQuesto bot ti permette di trovare le stazioni di servizio più vicine a te, con i prezzi aggiornati in tempo reale. \n\nPer iniziare, ho bisogno di farti alcune domande")
                        bot.sendMessage(chat_id, "Qual'è la capacità del tuo serbatoio?")
                        #aspetta che arrivi il messagio dell'utente
                        while(bot.checkForNewMessages(lastUpdateId) == False):
                            pass
                        updates = bot.getUpdates(lastUpdateId)

                        # capienza serbatoio
                        capeienza = int(updates['result'][-1]['message']['text'])
                        lastUpdateId = lastUpdateId + 1

                        bot.sendKeyboard(chat_id, "Qual'è il tipo di carburante che utilizzi?", [['Benzina'], ['Diesel'], ['Metano'], ['GPL']])
                        while(bot.checkForNewMessages(lastUpdateId) == False):
                            pass
                        updates = bot.getUpdates(lastUpdateId)
                        # tipo di carburante
                        tipoCarburante = updates['result'][-1]['message']['text']
                        lastUpdateId = lastUpdateId + 1

                        bot.sendMessage(chat_id, "Quanti km fai con un litro? (questo servirà per calcolare il benzinaio più conveniente)")
                        while(bot.checkForNewMessages(lastUpdateId) == False):
                            pass
                        
                        updates = bot.getUpdates(lastUpdateId)
                        # distanza con un litro di carburante
                        kmLitro = int(updates['result'][-1]['message']['text'])
                        bot.sendMessage(chat_id, "Qual'è il range di distanza entro cui vuoi cercare i benzinai? (in km)")
                        lastUpdateId = lastUpdateId + 1
                        
                        while(bot.checkForNewMessages(lastUpdateId) == False):
                            pass
                        updates = bot.getUpdates(lastUpdateId)
                        # entro quanti km voglio cercare un benzinaio
                        range = int(updates['result'][-1]['message']['text'])
                        lastUpdateId = lastUpdateId + 1
                        #inserimento delle info dell'utente nel database
                        mysql.execute(f"INSERT INTO utenti (idUtente, capacitaSerbatoio, tipoCarburante, kmLitro, maxRange) VALUES ({user_id}, {capeienza}, '{tipoCarburante}', {kmLitro}, {range})")
                        bot.sendMessage(chat_id, "Ok! Utente aggiunto")
                    else:
                        #avvio il bot non per la prima volta
                        bot.sendMessage(chat_id, "Bentornato su Benzinabot!")
                    
                    bot.sendKeyboard(chat_id, "Quanto carburante devi rifornire?", [[{"text": "1/4"}], [{"text": "2/4"}], [{"text": "3/4"}], [{"text": "4/4"}]])

                    while(bot.checkForNewMessages(lastUpdateId) == False):
                        pass
                    updates = bot.getUpdates(lastUpdateId)

                    # Quantità carburante - keyboard
                    carburanteQTYstr = updates['result'][-1]['message']['text']
                    lastUpdateId = lastUpdateId + 1
                    carburanteQTY = float(carburanteQTYstr.split("/")[0]) / float(carburanteQTYstr.split("/")[1])

                    # richiesta posizione
                    recPos = False
                    while (recPos == False):
                        bot.sendMessage(chat_id, "Per favore, inviami la tua posizione")
                        while(bot.checkForNewMessages(lastUpdateId) == False):
                            pass
                        updates = bot.getUpdates(lastUpdateId)
                        # posizione dell'utente, se il messaggio non è la condivisione della posizione viene richiesto all'utente
                        if 'location' in updates['result'][-1]['message']:
                            latitude = updates['result'][-1]['message']['location']['latitude']
                            longitude = updates['result'][-1]['message']['location']['longitude']
                            recPos = True
                        else :
                            bot.sendMessage(chat_id, "Per favore, rinviami la tua posizione")
                            continue
                    
                    # richiesta self service
                    lastUpdateId = lastUpdateId + 1
                    bot.sendKeyboard(chat_id, "Self service?", [["Si"], ["No"]])
                    while(bot.checkForNewMessages(lastUpdateId) == False):
                        pass
                    updates = bot.getUpdates(lastUpdateId)
                    if updates['result'][-1]['message']['text'] == "Si":
                        selfService = True
                    else:
                        selfService = False
                    lastUpdateId = lastUpdateId + 1

                    # trovo i cinque benzinai più vicini nel database
                    tipoCarburante = mysql.fetch(f"SELECT tipoCarburante FROM utenti WHERE idUtente = {user_id}")[0][0]
                    maxDistance = mysql.fetch(f"SELECT maxRange FROM utenti WHERE idUtente = {user_id}")[0][0]
                    bot.sendMessage(chat_id, "Sto cercando i benzinai più vicini...") 
                    bot.sendMessage(chat_id, humanHandler.getNearestStations(latitude, longitude, maxDistance, tipoCarburante, selfService, carburanteQTY, user_id), "parse_mode=Markdown")
                    bot.sendMessage(chat_id, "Tra le parentesi trovi il prezzo del carburante per il rifornimento, mentre prima trovi il prezzo complessivo del rifornimento e del costo del tragitto")
                    bot.sendMessage(chat_id, "Se vuoi cercare altri benzinai, scrivi [/start](/start) o scrivi [/reset](/reset) per riavviare la configurazione.", "parse_mode=Markdown")
                elif text == '/reset':
                    mysql.execute(f"DELETE FROM utenti WHERE idUtente = {user_id}")
                    bot.sendMessage(chat_id, "Utente rimosso, avvia una nuova conversazione con [/start](/start) !", "parse_mode=Markdown")
        time.sleep(5)
