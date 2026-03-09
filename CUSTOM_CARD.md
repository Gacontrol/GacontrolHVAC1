# GAControl Heating Group Card

Eine benutzerdefinierte Lovelace Card für GAControl HVAC Heizgruppen - vergleichbar mit der Climate Card für Thermostate.

## Features

- **Moderne Benutzeroberfläche** - Ansprechendes Design mit allen wichtigen Informationen auf einen Blick
- **Temperaturanzeige** - Aktuelle und Zieltemperatur übersichtlich dargestellt
- **Direkte Steuerung** - Temperatur und Modus direkt in der Card ändern
- **Status-Anzeige** - Visueller Indikator ob die Heizgruppe heizt, bereit oder aus ist
- **Ventilpositionen** - Grafische Anzeige aller Ventilpositionen mit Balkendiagramm
- **Visueller Editor** - Einfache Konfiguration über die UI

## Installation

Die Card wird automatisch mit der GAControl HVAC Integration installiert. Nach dem Neustart von Home Assistant steht sie sofort zur Verfügung.

## Verwendung

### Über die UI (Empfohlen)

1. Dashboard bearbeiten
2. "+ Card hinzufügen"
3. Im Suchfeld nach "GAControl" suchen
4. "GAControl Heating Group Card" auswählen
5. Heizgruppen-Entität auswählen
6. Optional: Name und Anzeigeoptionen anpassen

### YAML Konfiguration

```yaml
type: custom:gacontrol-heating-group-card
entity: climate.heating_group_erdgeschoss
```

### Erweiterte Konfiguration

```yaml
type: custom:gacontrol-heating-group-card
entity: climate.heating_group_erdgeschoss
name: "Erdgeschoss"
show_valves: true
```

## Konfigurationsoptionen

| Option | Typ | Pflicht | Standard | Beschreibung |
|--------|-----|---------|----------|--------------|
| `entity` | string | Ja | - | Die climate Entity ID der Heizgruppe |
| `name` | string | Nein | Entity Name | Überschreibt den Anzeigenamen |
| `show_valves` | boolean | Nein | `true` | Zeigt Ventilpositionen an |

## Beispiele

### Einzelne Heizgruppe

```yaml
type: custom:gacontrol-heating-group-card
entity: climate.heating_group_wohnzimmer
```

### Mehrere Heizgruppen in einer Ansicht

```yaml
type: grid
columns: 2
cards:
  - type: custom:gacontrol-heating-group-card
    entity: climate.heating_group_erdgeschoss

  - type: custom:gacontrol-heating-group-card
    entity: climate.heating_group_obergeschoss

  - type: custom:gacontrol-heating-group-card
    entity: climate.heating_group_keller
```

### Mit angepasstem Namen

```yaml
type: custom:gacontrol-heating-group-card
entity: climate.heating_group_erdgeschoss
name: "EG - Hauptheizkreis"
```

## Funktionen

### Temperatursteuerung

- **Plus/Minus Buttons** - Erhöhen/Verringern der Zieltemperatur
- **Schrittweite** - Verwendet die in der Heizgruppe konfigurierte Schrittweite
- **Min/Max Begrenzung** - Respektiert die konfigurierten Temperaturgrenzen

### Modus-Wechsel

- **Heizen** - Aktiviert die automatische Heizregelung
- **Aus** - Schaltet die Heizgruppe aus

### Status-Anzeige

Die Card zeigt den aktuellen Betriebszustand:

- **Heizen** (Orange) - Die Heizgruppe heizt aktiv
- **Bereit** (Grün) - Zieltemperatur erreicht, bereit zum Heizen
- **Aus** (Grau) - Heizgruppe ist ausgeschaltet

### Ventilpositionen

Wenn Ventile in der Heizgruppe konfiguriert sind, werden diese als Balkendiagramme angezeigt:

- Name des Ventils
- Visueller Balken (0-100%)
- Prozentangabe

## Troubleshooting

### Card wird nicht angezeigt

1. Home Assistant neustarten
2. Browser-Cache leeren (Strg+F5)
3. Logs prüfen: `custom_components.gacontrol_hvac`

### Entity nicht gefunden

Stellen Sie sicher, dass:
- Die GAControl HVAC Integration korrekt installiert ist
- Die Heizgruppe konfiguriert wurde
- Die Entity ID korrekt ist (z.B. `climate.heating_group_...`)

### Änderungen werden nicht übernommen

- Warten Sie 2-3 Sekunden nach der Änderung
- Prüfen Sie die Logs auf Fehler
- Stellen Sie sicher, dass die Heizgruppe nicht "unavailable" ist

## Design

Die Card folgt dem Home Assistant Design System:

- **Responsive** - Passt sich an verschiedene Bildschirmgrößen an
- **Theme-kompatibel** - Nutzt die konfigurierten Farben und Styles
- **Animationen** - Sanfte Übergänge und Hover-Effekte
- **Accessibility** - Klare Beschriftungen und gute Kontraste

## Technische Details

- **Typ**: `custom:gacontrol-heating-group-card`
- **Platform**: Lovelace Custom Card
- **Browser**: Alle modernen Browser (Chrome, Firefox, Safari, Edge)
- **Home Assistant**: 2024.1.0 oder neuer

## Support

Bei Problemen oder Fragen:
1. Logs prüfen
2. GitHub Issues erstellen
3. Community Forum nutzen
