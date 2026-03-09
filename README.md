# Gacontrol HVAC - Home Assistant Integration

Eine Home Assistant Custom Integration zur Steuerung und Überwachung von Heizgruppen mit automatischer Vorlauftemperaturregelung.

## Funktionen

### Heizgruppensteuerung
- **Automatische Vorlauftemperaturregelung** mit PI-Regler
- **Heizkennlinien-basierte Sollwertberechnung** abhängig von der Außentemperatur
- **Drei Betriebsarten**: Auto, Ein, Aus
- **Außentemperatur-Mittelung** über konfigurierbare Zeitspanne
- **Pumpenüberwachung** mit Betriebsmeldung und Störungserkennung
- **Sicherheitstemperaturbegrenzer** zum Schutz vor Übertemperatur

### Sensoren
Die Integration erstellt folgende Sensoren:
- Vorlauftemperatur
- Rücklauftemperatur
- Außentemperatur (aktuell)
- Außentemperatur (gemittelt)
- Vorlauf Sollwert
- Mischventil Position
- Reglerausgang
- Regelabweichung

### Binäre Sensoren
- System Status
- Pumpe Befehl
- Pumpe Betriebsmeldung
- Pumpenstörung
- Sicherheitstemperaturbegrenzer
- Gesamtstörung

### Steuerung
- **Climate Entity** für Hauptsteuerung (Auto/Heat/Off)
- **Switch** für Heizgruppen-Freigabe
- **Select Entity** für Betriebsmodus-Auswahl (auto, on, off)
- **Number Entities** für:
  - Temperatureingaben (Vorlauf, Rücklauf, Außen)
  - Heizkennlinie (Min/Max Vorlauf, Ein-/Ausschalttemperatur)
  - Regler-Parameter (P-Anteil, I-Anteil)
  - Pumpen-Verzögerung
- **Text Entities** für Entity-Verknüpfungen mit externen Sensoren und Ausgängen

## Installation

### HACS (empfohlen)

1. Öffnen Sie HACS in Home Assistant
2. Gehen Sie zu "Integrationen"
3. Klicken Sie auf die drei Punkte oben rechts und wählen Sie "Benutzerdefinierte Repositories"
4. Fügen Sie die Repository-URL hinzu: `https://github.com/Gacontrol/GacontrolHVAC`
5. Kategorie: Integration
6. Klicken Sie auf "Hinzufügen"
7. Suchen Sie nach "Gacontrol HVAC"
8. Klicken Sie auf "Herunterladen"
9. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie die neueste Version herunter
2. Kopieren Sie den Ordner `custom_components/gacontrol_hvac` in Ihr Home Assistant `config/custom_components` Verzeichnis
3. Starten Sie Home Assistant neu

## Konfiguration

### Über die UI

1. Gehen Sie zu "Einstellungen" → "Geräte & Dienste"
2. Klicken Sie auf "+ Integration hinzufügen"
3. Suchen Sie nach "Gacontrol HVAC"
4. Folgen Sie dem Konfigurationsassistenten

### Konfigurationsparameter

Bei der Einrichtung können folgende Parameter konfiguriert werden:

#### Temperaturgrenzen
- **Min. Vorlauftemperatur** (Standard: 25°C) - Minimal zulässige Vorlauftemperatur
- **Max. Vorlauftemperatur** (Standard: 65°C) - Maximal zulässige Vorlauftemperatur

#### Außentemperatur Schaltpunkte
- **Einschalttemperatur** (Standard: 15°C) - Außentemperatur unterhalb derer die Heizgruppe einschaltet
- **Ausschalttemperatur** (Standard: 18°C) - Außentemperatur oberhalb derer die Heizgruppe ausschaltet
- **Mittelungszeit** (Standard: 24h) - Zeitspanne zur Mittelwertbildung der Außentemperatur

#### Regler Parameter
- **P-Anteil** (Standard: 5.0) - Proportionalanteil des PI-Reglers
- **I-Anteil** (Standard: 0.5) - Integralanteil des PI-Reglers

#### Pumpenüberwachung
- **Pumpen Start Verzögerung** (Standard: 10s) - Zeit bis zur Überprüfung der Pumpenbetriebsmeldung

## Verwendung

### Betriebsarten

#### Auto-Modus
Im Automatikbetrieb schaltet die Heizgruppe basierend auf der gemittelten Außentemperatur:
- **EIN** wenn Außentemperatur < Einschalttemperatur
- **AUS** wenn Außentemperatur > Ausschalttemperatur

#### Ein-Modus
Die Heizgruppe läuft dauerhaft, unabhängig von der Außentemperatur.

#### Aus-Modus
Die Heizgruppe ist ausgeschaltet.

### Heizkennlinie

Die Vorlaufsolltemperatur wird automatisch aus der gemittelten Außentemperatur berechnet:
- Bei hohen Außentemperaturen → niedrige Vorlauftemperatur (Min)
- Bei niedrigen Außentemperaturen → hohe Vorlauftemperatur (Max)

Der Sollwert wird linear zwischen Min und Max interpoliert.

### PI-Regler

Ein PI-Regler passt die Mischventilstellung kontinuierlich an, um die Vorlauftemperatur auf den Sollwert zu regeln:
- **P-Anteil**: Reagiert proportional zur aktuellen Abweichung
- **I-Anteil**: Eliminiert bleibende Regelabweichung über die Zeit

### Störungsmeldungen

Das System erkennt automatisch folgende Störungen:
- **Pumpenstörung**: Pumpen-Fault-Signal aktiv
- **Keine Betriebsmeldung**: Pumpe läuft nicht nach Startbefehl
- **Sicherheitstemperaturbegrenzer**: Übertemperatur erkannt

Bei aktiver Störung wird die Heizgruppe in einen sicheren Zustand versetzt.

## Automatisierung Beispiele

### Außentemperatur von Wetterstation verwenden

```yaml
automation:
  - alias: "Heizgruppe - Außentemperatur aktualisieren"
    trigger:
      - platform: state
        entity_id: sensor.wetterstation_temperatur
    action:
      - service: number.set_value
        target:
          entity_id: number.heizgruppe_1_aussentemperatur_eingabe
        data:
          value: "{{ states('sensor.wetterstation_temperatur') }}"
```

### Sensoren verknüpfen (iSMA Integration)

Sie können externe Sensoren und Ausgänge direkt über Text-Entities verknüpfen:

1. Öffnen Sie die Text-Entity (z.B. `text.heizgruppe_1_vorlauftemperatur_entity`)
2. Geben Sie die Entity-ID Ihres Sensors ein (z.B. `sensor.isma_vorlauf_temp`)
3. Die Integration liest automatisch die Werte aus

**Verknüpfbare Eingänge:**
- Vorlauftemperatur Sensor
- Rücklauftemperatur Sensor
- Außentemperatur Sensor
- Pumpen-Rückmeldung (binary_sensor)
- Pumpenstörung (binary_sensor)
- Sicherheitstemperaturbegrenzer (binary_sensor)

**Verknüpfbare Ausgänge:**
- Pumpen Ausgang (switch)
- Ventil AUF Ausgang (switch)
- Ventil ZU Ausgang (switch)

**Hinweis:** Wenn keine externen Entities verknüpft sind, können Sie die manuellen Number-Eingaben verwenden.

### Benachrichtigung bei Störung

```yaml
automation:
  - alias: "Heizgruppe - Störungsbenachrichtigung"
    trigger:
      - platform: state
        entity_id: binary_sensor.heizgruppe_1_storung
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Heizgruppe Störung"
          message: "Die Heizgruppe hat eine Störung erkannt!"
```

## Custom Lovelace Card

Die Integration enthält eine benutzerdefinierte Lovelace Card für die Heizgruppen-Darstellung!

**GAControl Heating Group Card** - Eine moderne Card ähnlich der Climate Card, speziell für Heizgruppen designed.

Detaillierte Dokumentation finden Sie in der Datei `CUSTOM_CARD.md`.

### Schnellstart

Nach der Installation der Integration können Sie die Card direkt verwenden:

```yaml
type: custom:gacontrol-heating-group-card
entity: climate.heizgruppe_1
```

Die Card bietet:
- Übersichtliche Temperaturanzeige (Aktuell & Ziel)
- Direkte Temperatursteuerung mit +/- Buttons
- Modus-Umschaltung (Heizen/Aus)
- Status-Anzeige mit Farb-Codierung
- Grafische Darstellung aller Ventilpositionen
- Visueller Editor für einfache Konfiguration

## Dashboard Beispiel

Eine vollständige Dashboard-Konfiguration mit allen Parametern finden Sie in der Datei `lovelace_dashboard_example.yaml`.

**Einfaches Dashboard:**

```yaml
type: entities
title: Heizgruppe 1
entities:
  - entity: climate.heizgruppe_1
  - entity: switch.heizgruppe_1_freigabe
  - entity: select.heizgruppe_1_betriebsmodus
  - type: divider
  - entity: sensor.heizgruppe_1_vorlauftemperatur
  - entity: sensor.heizgruppe_1_vorlauf_sollwert
  - entity: sensor.heizgruppe_1_rucklauftemperatur
  - entity: sensor.heizgruppe_1_aussentemperatur_gemittelt
  - type: divider
  - entity: sensor.heizgruppe_1_mischventil_position
  - entity: binary_sensor.heizgruppe_1_pumpe_befehl
  - entity: binary_sensor.heizgruppe_1_storung
```

**Parameter-Anpassung:**

Alle Heizkennlinien-Parameter und Regler-Einstellungen können direkt über Number-Entities auf dem Dashboard angepasst werden:

```yaml
type: entities
title: Heizkennlinie
entities:
  - entity: number.heizgruppe_1_min_vorlauftemperatur
  - entity: number.heizgruppe_1_max_vorlauftemperatur
  - entity: number.heizgruppe_1_einschalttemperatur
  - entity: number.heizgruppe_1_ausschalttemperatur
```

## Technische Details

### Regelung

Die Vorlauftemperatur wird mit einem digitalen PI-Regler geregelt:

```
error = setpoint - actual_temperature
P = Kp × error
I = Ki × ∫error dt
output = P + I (begrenzt auf 0-100%)
```

Die Regelung läuft alle 2 Sekunden.

### Heizkennlinie

```
wenn outside_temp_avg ≥ outside_temp_off:
    setpoint = min_supply_temp

sonst:
    ratio = (outside_temp_off - outside_temp_avg) / (outside_temp_off - (-20°C))
    setpoint = min_supply_temp + ratio × (max_supply_temp - min_supply_temp)
```

### Außentemperatur-Mittelung

Die Außentemperatur wird über die konfigurierte Zeitspanne gemittelt (Standard: 24h).
Alle eingehenden Werte werden gespeichert und für die Mittelwertbildung verwendet.

## Support

Bei Fragen oder Problemen erstellen Sie bitte ein Issue auf GitHub:
https://github.com/Gacontrol/GacontrolHVAC/issues

## Lizenz

MIT License

Copyright (c) 2026 Gacontrol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
