# Gacontrol HVAC

Eine professionelle Home Assistant Integration zur Steuerung von Heizgruppen mit automatischer Vorlauftemperaturregelung.

## Hauptfunktionen

- **PI-Regelung** der Vorlauftemperatur
- **Heizkennlinie** basierte Sollwertberechnung
- **Außentemperatur-Mittelung** über konfigurierbare Zeitspanne
- **Drei Betriebsarten**: Auto, Ein, Aus
- **Pumpenüberwachung** mit Störungserkennung
- **Sicherheitstemperaturbegrenzer**

## Was wird erstellt?

Nach der Installation werden folgende Entities erstellt:

### Climate
- Hauptsteuerung mit Auto/Heat/Off Modi

### Sensoren
- Vorlauftemperatur
- Rücklauftemperatur
- Außentemperatur (aktuell & gemittelt)
- Vorlauf Sollwert
- Mischventil Position
- Reglerausgang & Regelabweichung

### Binäre Sensoren
- System Status
- Pumpe (Befehl & Betrieb)
- Störungsmeldungen

### Steuerung
- Freigabe Switch
- Temperatur Number Inputs

## Konfiguration

Bei der Ersteinrichtung können alle Parameter wie Temperaturgrenzwerte, Schaltpunkte und Reglerparameter konfiguriert werden.

Die Parameter können später jederzeit über die Optionen angepasst werden.
