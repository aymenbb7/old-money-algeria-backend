import re

with open("dashboard/templates/dashboard/settings.html", "r", encoding="utf-8") as f:
    content = f.read()

theme_html = """
    <!-- Appearance & Theme -->
    <div class="settings-card" style="grid-column: 1 / -1;">
        <h3 class="settings-header">Apparence & Thème</h3>
        <form id="themeForm" onsubmit="saveTheme(event)">
            <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:1.5rem; margin-bottom: 1.5rem;" id="themeOptions">
                <!-- Theme cards will be injected here via JS to avoid repetition -->
            </div>
            
            <div id="customThemeSettings" style="display:none; margin-top: 1.5rem; border-top: 1px solid var(--border-color); padding-top: 1.5rem;">
                <h4 style="color: var(--accent-gold); margin-bottom: 1rem;">Couleurs Personnalisées</h4>
                <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap:1rem;">
                    <div class="form-group">
                        <label>Couleur Principale (Primary)</label>
                        <input type="color" id="customPrimary" class="form-control" style="height: 50px; padding: 0.2rem;">
                    </div>
                    <div class="form-group">
                        <label>Couleur de fond (Bg)</label>
                        <input type="color" id="customBg" class="form-control" style="height: 50px; padding: 0.2rem;">
                    </div>
                    <div class="form-group">
                        <label>Couleur d'accent (Accent)</label>
                        <input type="color" id="customAccent" class="form-control" style="height: 50px; padding: 0.2rem;">
                    </div>
                    <div class="form-group">
                        <label>Couleur des cartes (Cards)</label>
                        <input type="color" id="customCards" class="form-control" style="height: 50px; padding: 0.2rem;">
                    </div>
                    <div class="form-group">
                        <label>Couleur du texte (Text)</label>
                        <input type="color" id="customText" class="form-control" style="height: 50px; padding: 0.2rem;">
                    </div>
                </div>
            </div>
            
            <button type="submit" class="btn-save">Enregistrer le Thème</button>
            <div style="clear:both;"></div>
        </form>
    </div>
"""

content = content.replace("</div>\n{% endblock %}", theme_html + "\n</div>\n{% endblock %}")

js_code = """
    const THEMES = {
        'dark-classique': {name: 'Dark Classique', bg: '#0A0A0A', text: '#F5F0E8', accent: '#D4AF37', cards: '#1A1A1A', primary: '#1B5E20'},
        'green-luxury': {name: 'Green Luxury', bg: '#0D2B0D', text: '#F5F0E8', accent: '#D4AF37', cards: '#1A3D1A', primary: '#1B5E20'},
        'forest-gold': {name: 'Forest & Gold', bg: '#1B3A1B', text: '#FFFFFF', accent: '#D4AF37', cards: '#243D24', primary: '#2E7D32'},
        'black-green': {name: 'Black & Green', bg: '#0A0A0A', text: '#FFFFFF', accent: '#2E7D32', cards: '#111111', primary: '#2E7D32'},
        'gold-dark': {name: 'Gold & Dark', bg: '#1A1400', text: '#F5F0E8', accent: '#D4AF37', cards: '#2A2000', primary: '#8D6E00'},
        'pure-green': {name: 'Pure Green', bg: '#1B5E20', text: '#FFFFFF', accent: '#D4AF37', cards: '#2E7D32', primary: '#1B5E20'},
        'custom': {name: 'Custom Theme', bg: '#0A0A0A', text: '#F5F0E8', accent: '#D4AF37', cards: '#1A1A1A', primary: '#1B5E20'}
    };

    function renderThemeCards() {
        const container = document.getElementById('themeOptions');
        let html = '';
        for (const [key, t] of Object.entries(THEMES)) {
            html += `
                <div class="theme-card" id="theme-card-${key}" onclick="selectTheme('${key}')" style="cursor: pointer; border: 2px solid transparent; border-radius: 8px; padding: 1rem; background: ${t.bg}; color: ${t.text}; text-align: center; transition: all 0.3s;">
                    <div style="font-weight: bold; margin-bottom: 0.5rem; font-family: 'Playfair Display', serif;">${t.name}</div>
                    <div style="display: flex; gap: 0.5rem; justify-content: center;">
                        <div style="width: 20px; height: 20px; border-radius: 50%; background: ${t.primary}; border: 1px solid #fff;"></div>
                        <div style="width: 20px; height: 20px; border-radius: 50%; background: ${t.accent}; border: 1px solid #fff;"></div>
                        <div style="width: 20px; height: 20px; border-radius: 50%; background: ${t.cards}; border: 1px solid #fff;"></div>
                    </div>
                </div>
            `;
        }
        container.innerHTML = html;
    }

    function selectTheme(themeKey) {
        // Remove active class
        document.querySelectorAll('.theme-card').forEach(el => {
            el.style.borderColor = 'transparent';
        });
        // Set active class
        const activeCard = document.getElementById(`theme-card-${themeKey}`);
        if(activeCard) activeCard.style.borderColor = '#D4AF37'; // gold border for selection

        // Show/hide custom options
        const customDiv = document.getElementById('customThemeSettings');
        if (themeKey === 'custom') {
            customDiv.style.display = 'block';
            applyCustomThemePreview(); // apply current picker values
        } else {
            customDiv.style.display = 'none';
            applyThemePreview(themeKey);
        }

        // Store selected theme in a hidden input or global var
        window.selectedTheme = themeKey;
    }

    function applyThemePreview(themeKey) {
        const t = THEMES[themeKey];
        document.documentElement.style.setProperty('--color-bg', t.bg);
        document.documentElement.style.setProperty('--color-text', t.text);
        document.documentElement.style.setProperty('--color-accent', t.accent);
        document.documentElement.style.setProperty('--color-cards', t.cards);
        document.documentElement.style.setProperty('--color-primary', t.primary);
        
        // Also apply to dashboard specific vars for live preview in admin
        document.documentElement.style.setProperty('--bg-color', t.bg);
        document.documentElement.style.setProperty('--text-main', t.text);
        document.documentElement.style.setProperty('--accent-gold', t.accent);
        document.documentElement.style.setProperty('--card-color', t.cards);
    }

    function applyCustomThemePreview() {
        if(window.selectedTheme !== 'custom') return;
        const bg = document.getElementById('customBg').value;
        const text = document.getElementById('customText').value;
        const accent = document.getElementById('customAccent').value;
        const cards = document.getElementById('customCards').value;
        const primary = document.getElementById('customPrimary').value;
        
        document.documentElement.style.setProperty('--color-bg', bg);
        document.documentElement.style.setProperty('--color-text', text);
        document.documentElement.style.setProperty('--color-accent', accent);
        document.documentElement.style.setProperty('--color-cards', cards);
        document.documentElement.style.setProperty('--color-primary', primary);
        
        document.documentElement.style.setProperty('--bg-color', bg);
        document.documentElement.style.setProperty('--text-main', text);
        document.documentElement.style.setProperty('--accent-gold', accent);
        document.documentElement.style.setProperty('--card-color', cards);
    }

    // Add listeners to custom inputs
    document.addEventListener('DOMContentLoaded', () => {
        renderThemeCards();
        ['customBg', 'customText', 'customAccent', 'customCards', 'customPrimary'].forEach(id => {
            const el = document.getElementById(id);
            if(el) el.addEventListener('input', applyCustomThemePreview);
        });
    });

    async function saveTheme(e) {
        e.preventDefault();
        if(!settingsId) return alert('Settings not loaded yet.');
        
        const formData = new FormData();
        formData.append('active_theme', window.selectedTheme || 'dark-classique');
        
        if (window.selectedTheme === 'custom') {
            formData.append('custom_bg_color', document.getElementById('customBg').value);
            formData.append('custom_text_color', document.getElementById('customText').value);
            formData.append('custom_accent_color', document.getElementById('customAccent').value);
            formData.append('custom_cards_color', document.getElementById('customCards').value);
            formData.append('custom_primary_color', document.getElementById('customPrimary').value);
        }

        try {
            const token = localStorage.getItem('oma_access_token');
            const res = await fetch(`/api/v1/settings/${settingsId}/`, {
                method: 'PATCH',
                headers: { 'Authorization': `Bearer ${token}` },
                body: formData
            });
            if (res.ok) alert(`Theme saved successfully.`);
            else alert(`Error saving theme settings.`);
        } catch(err) {
            alert('Network error');
        }
    }
"""

content = content.replace("document.getElementById('googleAnalytics').value = s.google_analytics_id || '';", 
    "document.getElementById('googleAnalytics').value = s.google_analytics_id || '';\n            window.selectedTheme = s.active_theme || 'dark-classique';\n            document.getElementById('customBg').value = s.custom_bg_color || '#0A0A0A';\n            document.getElementById('customText').value = s.custom_text_color || '#F5F0E8';\n            document.getElementById('customAccent').value = s.custom_accent_color || '#D4AF37';\n            document.getElementById('customCards').value = s.custom_cards_color || '#1A1A1A';\n            document.getElementById('customPrimary').value = s.custom_primary_color || '#1B5E20';\n            selectTheme(window.selectedTheme);")

content = content.replace("let heroId = null;", "let heroId = null;\n" + js_code)

with open("dashboard/templates/dashboard/settings.html", "w", encoding="utf-8") as f:
    f.write(content)
