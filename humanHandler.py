import dbHandler
import requestHandler
requestHandler = requestHandler.rh()
mysql = dbHandler.ch("localhost", "root", "", "benzinabot")

class humanHandler:
    def getNearestStations(self, lat, lon, max_distance, tipo_carburante, is_self, carburanteQTY, idUtente):
        # trovo i tre benzinai più vicini nel database, 10 benzinai in linea d'aria
        query = f"""
        SELECT a.Bandiera, a.Latitudine, a.Longitudine, p.prezzo, 
            (6371 * acos(cos(radians({lat})) * cos(radians(a.Latitudine)) * cos(radians(a.Longitudine) - radians({lon})) + sin(radians({lat})) * sin(radians(a.Latitudine)))) AS Distanza
        FROM anagrafica a   
        JOIN prezzi p ON a.idImpianto = p.idImpianto
        WHERE p.descCarburante = '{tipo_carburante}' AND p.isSelf = {int(is_self)}
            AND (6371 * acos(cos(radians({lat})) * cos(radians(a.Latitudine)) * cos(radians(a.Longitudine) - radians({lon})) + sin(radians({lat})) * sin(radians(a.Latitudine)))) < {max_distance}
        ORDER BY prezzo ASC
        LIMIT 500
        """
        result = mysql.fetch(query)

        # prendo i dati per calcolare la convenienza
        capacitaSerbatoio = mysql.fetch(f"SELECT capacitaSerbatoio FROM utenti WHERE idUtente = {idUtente}")[0][0]
        consumo = mysql.fetch(f"SELECT kmLitro FROM utenti WHERE idUtente = {idUtente}")[0][0]

        updatedResults = []
        # calcolo costo con la distanza punto - punto
        for r in result:
            r = list(r)
            prezzo = (r[3] * (capacitaSerbatoio * carburanteQTY)) + (2*((r[4] / consumo) * r[3]))
            r.append(round(prezzo, 4))
            updatedResults.append(r)

        result = sorted(updatedResults, key=lambda x: x[5])
        result = updatedResults[:5]
        result = [r[:-1] for r in result]

        # con i 5 fai ulteriore recerca per il migliore
        updatedResults = []
        for r in result:
            r = list(r)
            latImp = r[1]   
            lonImp = r[2]
            summary = requestHandler.getOSRdistance(lat, lon, latImp, lonImp)
            r[4] = int(summary['distance'])/1000
            minuti = summary['duration'] // 60
            secondi = int(summary['duration'] % 60)
            r.append(f"{int(minuti):02d}:{secondi:02d}")
            updatedResults.append(r)

        # calcolo il benzinaio più conveniente tra quelli restituiti dalla query 
        for ur in updatedResults:
            ur[4] = round(ur[4], 2)
            prezzonorm = ur[3] * (capacitaSerbatoio * carburanteQTY)
            prezzotot = prezzonorm + ((ur[4] / consumo) * ur[3])
            mapslink = f"https://www.google.com/maps/dir/{lat},{lon}/{latImp},{lonImp}"
            ur.append(round(prezzonorm, 2))
            ur.append(round(prezzotot, 2))
            ur.append(mapslink)
                        
        for ur in updatedResults:
            ur[4] = str(ur[4]) + " km"
            ur[5] = str(ur[5]) + " min"

        
        updatedResults = sorted(updatedResults, key=lambda x: x[7])

        i = 0
        msg = ""
        for ur in updatedResults:  
            msg += str(i+1) + ". [" + str(updatedResults[i][0]) + "](" + str(updatedResults[i][8]) + ")" + "\n" + "Prezzo/L " + str(updatedResults[i][3]) + "€ - Prezzo: " + str(updatedResults[i][7]) + "€ (" + str(updatedResults[i][6]) + "€)" + "\n" + "Distanza: " + str(updatedResults[i][4]) + " - Tempo: " + str(updatedResults[i][5]) + "\n"
            i += 1

        if msg == "":
            msg = "Nessun risultato trovato"
        return msg
