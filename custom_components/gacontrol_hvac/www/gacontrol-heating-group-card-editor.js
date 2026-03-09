class GacontrolHeatingGroupCardEditor extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this.render();
  }

  set hass(hass) {
    this._hass = hass;
  }

  get hass() {
    return this._hass;
  }

  render() {
    if (!this._hass) return;

    if (!this.content) {
      const card = document.createElement('ha-card');
      card.style.padding = '16px';
      this.appendChild(card);
      this.content = card;
    }

    const entities = Object.keys(this._hass.states).filter(
      entity => entity.startsWith('climate.')
    );

    this.content.innerHTML = `
      <style>
        .config-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 16px;
        }
        .config-label {
          font-weight: 500;
          margin-right: 16px;
        }
        .config-input {
          flex: 1;
          max-width: 300px;
        }
        ha-select, ha-textfield {
          width: 100%;
        }
        .description {
          color: var(--secondary-text-color);
          font-size: 12px;
          margin-top: 4px;
        }
      </style>

      <div class="config-row">
        <div>
          <div class="config-label">Entity</div>
          <div class="description">Wählen Sie die Heizgruppen-Entität</div>
        </div>
        <div class="config-input">
          <select id="entity-select" style="width: 100%; padding: 8px;">
            <option value="">-- Entität wählen --</option>
            ${entities.map(entity => `
              <option value="${entity}" ${this._config.entity === entity ? 'selected' : ''}>
                ${this._hass.states[entity].attributes.friendly_name || entity}
              </option>
            `).join('')}
          </select>
        </div>
      </div>

      <div class="config-row">
        <div>
          <div class="config-label">Name (Optional)</div>
          <div class="description">Überschreibt den Standard-Namen</div>
        </div>
        <div class="config-input">
          <input
            type="text"
            id="name-input"
            value="${this._config.name || ''}"
            placeholder="Eigener Name"
            style="width: 100%; padding: 8px; box-sizing: border-box;"
          />
        </div>
      </div>

      <div class="config-row">
        <div>
          <div class="config-label">Ventile anzeigen</div>
          <div class="description">Zeigt Ventilpositionen an</div>
        </div>
        <div class="config-input">
          <label style="display: flex; align-items: center; cursor: pointer;">
            <input
              type="checkbox"
              id="show-valves"
              ${this._config.show_valves !== false ? 'checked' : ''}
              style="margin-right: 8px;"
            />
            Aktiviert
          </label>
        </div>
      </div>
    `;

    this.content.querySelector('#entity-select').addEventListener('change', (e) => {
      this._config = { ...this._config, entity: e.target.value };
      this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: this._config } }));
    });

    const nameInput = this.content.querySelector('#name-input');
    nameInput.addEventListener('input', (e) => {
      this._config = { ...this._config, name: e.target.value };
      this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: this._config } }));
    });

    this.content.querySelector('#show-valves').addEventListener('change', (e) => {
      this._config = { ...this._config, show_valves: e.target.checked };
      this.dispatchEvent(new CustomEvent('config-changed', { detail: { config: this._config } }));
    });
  }
}

customElements.define('gacontrol-heating-group-card-editor', GacontrolHeatingGroupCardEditor);
