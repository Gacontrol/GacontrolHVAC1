class GacontrolHeatingGroupCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('You need to define an entity');
    }
    this.config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    this.updateCard();
  }

  get hass() {
    return this._hass;
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        ha-card {
          padding: 16px;
          position: relative;
        }
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        .header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .group-icon {
          --mdc-icon-size: 40px;
          color: var(--primary-color);
        }
        .group-name {
          font-size: 24px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .status-badge {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
          text-transform: uppercase;
        }
        .status-heating {
          background: rgba(255, 152, 0, 0.2);
          color: #ff9800;
        }
        .status-idle {
          background: rgba(76, 175, 80, 0.2);
          color: #4caf50;
        }
        .status-off {
          background: rgba(158, 158, 158, 0.2);
          color: #9e9e9e;
        }
        .temperature-display {
          display: flex;
          justify-content: space-around;
          margin: 24px 0;
          gap: 16px;
        }
        .temp-box {
          flex: 1;
          text-align: center;
          padding: 16px;
          background: var(--secondary-background-color);
          border-radius: 12px;
        }
        .temp-label {
          font-size: 12px;
          color: var(--secondary-text-color);
          text-transform: uppercase;
          margin-bottom: 8px;
        }
        .temp-value {
          font-size: 32px;
          font-weight: 300;
          color: var(--primary-text-color);
        }
        .temp-unit {
          font-size: 18px;
          color: var(--secondary-text-color);
        }
        .controls-section {
          margin: 20px 0;
        }
        .control-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 0;
          border-bottom: 1px solid var(--divider-color);
        }
        .control-row:last-child {
          border-bottom: none;
        }
        .control-label {
          font-size: 14px;
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .control-value {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .temp-controls {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        .temp-button {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          border: 2px solid var(--primary-color);
          background: transparent;
          color: var(--primary-color);
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }
        .temp-button:hover {
          background: var(--primary-color);
          color: white;
        }
        .temp-button:active {
          transform: scale(0.95);
        }
        .temp-input {
          width: 60px;
          text-align: center;
          font-size: 18px;
          font-weight: 500;
          color: var(--primary-text-color);
        }
        .switch-control {
          position: relative;
          width: 48px;
          height: 24px;
        }
        .switch-control input {
          opacity: 0;
          width: 0;
          height: 0;
        }
        .slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: var(--divider-color);
          transition: .3s;
          border-radius: 24px;
        }
        .slider:before {
          position: absolute;
          content: "";
          height: 18px;
          width: 18px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: .3s;
          border-radius: 50%;
        }
        input:checked + .slider {
          background-color: var(--primary-color);
        }
        input:checked + .slider:before {
          transform: translateX(24px);
        }
        .valves-section {
          margin-top: 20px;
        }
        .section-title {
          font-size: 14px;
          font-weight: 500;
          color: var(--secondary-text-color);
          margin-bottom: 12px;
          text-transform: uppercase;
        }
        .valve-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 0;
        }
        .valve-name {
          font-size: 14px;
          color: var(--primary-text-color);
        }
        .valve-bar {
          flex: 1;
          max-width: 200px;
          height: 8px;
          background: var(--divider-color);
          border-radius: 4px;
          margin: 0 12px;
          overflow: hidden;
        }
        .valve-bar-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
          transition: width 0.3s;
        }
        .valve-percentage {
          font-size: 14px;
          font-weight: 500;
          color: var(--primary-text-color);
          min-width: 45px;
          text-align: right;
        }
        .mode-selector {
          display: flex;
          gap: 8px;
        }
        .mode-button {
          padding: 6px 12px;
          border-radius: 8px;
          border: 2px solid var(--divider-color);
          background: transparent;
          color: var(--primary-text-color);
          cursor: pointer;
          font-size: 12px;
          transition: all 0.2s;
        }
        .mode-button.active {
          border-color: var(--primary-color);
          background: var(--primary-color);
          color: white;
        }
        .mode-button:hover:not(.active) {
          border-color: var(--primary-color);
        }
        ha-icon {
          --mdc-icon-size: 20px;
        }
        .unavailable {
          opacity: 0.5;
        }
      </style>
      <ha-card>
        <div id="card-content"></div>
      </ha-card>
    `;
    this.content = this.shadowRoot.getElementById('card-content');
  }

  updateCard() {
    if (!this._hass || !this.config) return;

    const entity = this._hass.states[this.config.entity];
    if (!entity) {
      this.content.innerHTML = `<div>Entity ${this.config.entity} not found</div>`;
      return;
    }

    const isUnavailable = entity.state === 'unavailable';
    const currentTemp = entity.attributes.current_temperature || 0;
    const targetTemp = entity.attributes.temperature || 0;
    const hvacAction = entity.attributes.hvac_action || 'idle';
    const hvacMode = entity.state || 'off';
    const valves = entity.attributes.valve_positions || {};

    const statusClass = hvacAction === 'heating' ? 'status-heating' :
                       hvacAction === 'idle' ? 'status-idle' : 'status-off';
    const statusText = hvacAction === 'heating' ? 'Heizen' :
                      hvacAction === 'idle' ? 'Bereit' : 'Aus';

    const valveEntries = Object.entries(valves);

    this.content.innerHTML = `
      <div class="${isUnavailable ? 'unavailable' : ''}">
        <div class="card-header">
          <div class="header-left">
            <ha-icon class="group-icon" icon="mdi:radiator"></ha-icon>
            <div class="group-name">${entity.attributes.friendly_name || 'Heizgruppe'}</div>
          </div>
          <div class="status-badge ${statusClass}">${statusText}</div>
        </div>

        <div class="temperature-display">
          <div class="temp-box">
            <div class="temp-label">Aktuell</div>
            <div class="temp-value">
              ${currentTemp.toFixed(1)}<span class="temp-unit">°C</span>
            </div>
          </div>
          <div class="temp-box">
            <div class="temp-label">Ziel</div>
            <div class="temp-value">
              ${targetTemp.toFixed(1)}<span class="temp-unit">°C</span>
            </div>
          </div>
        </div>

        <div class="controls-section">
          <div class="control-row">
            <div class="control-label">
              <ha-icon icon="mdi:thermostat"></ha-icon>
              Zieltemperatur
            </div>
            <div class="temp-controls">
              <button class="temp-button" data-action="decrease">
                <ha-icon icon="mdi:minus"></ha-icon>
              </button>
              <span class="temp-input">${targetTemp.toFixed(1)}°C</span>
              <button class="temp-button" data-action="increase">
                <ha-icon icon="mdi:plus"></ha-icon>
              </button>
            </div>
          </div>

          <div class="control-row">
            <div class="control-label">
              <ha-icon icon="mdi:power"></ha-icon>
              Modus
            </div>
            <div class="mode-selector">
              <button class="mode-button ${hvacMode === 'heat' ? 'active' : ''}" data-mode="heat">
                Heizen
              </button>
              <button class="mode-button ${hvacMode === 'off' ? 'active' : ''}" data-mode="off">
                Aus
              </button>
            </div>
          </div>
        </div>

        ${valveEntries.length > 0 ? `
          <div class="valves-section">
            <div class="section-title">Ventilpositionen</div>
            ${valveEntries.map(([name, value]) => `
              <div class="valve-item">
                <div class="valve-name">${name}</div>
                <div class="valve-bar">
                  <div class="valve-bar-fill" style="width: ${value}%"></div>
                </div>
                <div class="valve-percentage">${value}%</div>
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    `;

    this.shadowRoot.querySelectorAll('.temp-button').forEach(btn => {
      btn.addEventListener('click', () => this.handleTempChange(btn.dataset.action));
    });

    this.shadowRoot.querySelectorAll('.mode-button').forEach(btn => {
      btn.addEventListener('click', () => this.handleModeChange(btn.dataset.mode));
    });
  }

  handleTempChange(action) {
    const entity = this._hass.states[this.config.entity];
    if (!entity) return;

    const currentTemp = entity.attributes.temperature || 20;
    const step = entity.attributes.target_temp_step || 0.5;
    const newTemp = action === 'increase' ? currentTemp + step : currentTemp - step;

    const min = entity.attributes.min_temp || 5;
    const max = entity.attributes.max_temp || 35;
    const clampedTemp = Math.max(min, Math.min(max, newTemp));

    this._hass.callService('climate', 'set_temperature', {
      entity_id: this.config.entity,
      temperature: clampedTemp
    });
  }

  handleModeChange(mode) {
    this._hass.callService('climate', 'set_hvac_mode', {
      entity_id: this.config.entity,
      hvac_mode: mode
    });
  }

  getCardSize() {
    return 5;
  }

  static getConfigElement() {
    return document.createElement("gacontrol-heating-group-card-editor");
  }

  static getStubConfig() {
    return {
      entity: "climate.heating_group"
    };
  }
}

customElements.define('gacontrol-heating-group-card', GacontrolHeatingGroupCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'gacontrol-heating-group-card',
  name: 'GAControl Heating Group Card',
  description: 'Eine anpassbare Card für GAControl Heizgruppen'
});
