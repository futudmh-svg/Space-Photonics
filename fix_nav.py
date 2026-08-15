#!/usr/bin/env python3
"""
Add proper hamburger navigation for mobile and further UI polish.
"""

import os

hamburger_css = '''
        /* ─── Hamburger Navigation ─── */
        .nav-hamburger {
            display: none;
            position: fixed; top: 8px; left: 8px; z-index: 300;
            background: rgba(5,8,17,0.92); border: 1px solid #00d4aa;
            color: #00d4aa; padding: 8px 12px; border-radius: 8px;
            cursor: pointer; font-size: 1.2em;
        }
        .nav-overlay {
            display: none; position: fixed; inset: 0; z-index: 250;
            background: rgba(5,8,17,0.95); backdrop-filter: blur(12px);
            flex-direction: column; align-items: center; justify-content: center;
            gap: 8px; padding: 20px;
        }
        .nav-overlay.active { display: flex; }
        .nav-overlay a {
            color: #90e0ef; text-decoration: none; padding: 10px 20px;
            font-size: 1.1em; border-radius: 8px;
            background: rgba(13,27,42,0.7); border: 1px solid rgba(65,90,119,0.3);
            width: 200px; text-align: center;
        }
        .nav-overlay a:hover { background: #00d4aa; color: #050811; }
        .nav-close {
            position: absolute; top: 8px; right: 8px;
            color: #e63946; font-size: 1.5em; cursor: pointer;
            background: none; border: none; padding: 8px;
        }
        @media (max-width: 768px) {
            nav { display: none; }
            .nav-hamburger { display: block; }
        }
'''

hamburger_html = '''
    <button class="nav-hamburger" id="nav-hamburger">☰</button>
    <div class="nav-overlay" id="nav-overlay">
        <button class="nav-close" id="nav-close">✕</button>
        <a href="../index.html">🏠 Dashboard</a>
        <a href="../pages/architecture.html">🏛️ Architecture</a>
        <a href="../pages/digital-twin.html">🎮 3D Twin</a>
        <a href="../pages/opa-analysis.html">📡 OPA</a>
        <a href="../pages/link-budget.html">📊 Link Budget</a>
        <a href="../pages/hypersonic.html">🚀 Hypersonic</a>
        <a href="../pages/vleo-constellation.html">🌐 VLEO</a>
        <a href="../pages/mapper-3d.html">🗺️ Mapper</a>
        <a href="../pages/satellite-digital-twin.html">🛰️ Sat Twin</a>
        <a href="../pages/interception-mission.html">🎯 Intercept</a>
        <a href="../pages/vehicle-terminal.html">🛰️ Terminal</a>
        <a href="../pages/ehf-optical-trade.html">📡 EHF vs Opt</a>
        <a href="../pages/ppln-calculator.html">🔢 PPLN</a>
        <a href="../pages/research-gaps.html">🔬 Gaps</a>
        <a href="../pages/foundry.html">🏭 Foundry</a>
        <a href="../pages/foundry-cleanroom.html">🏭 Clean Room</a>
    </div>
'''

hamburger_js = '''
        // Hamburger nav
        const hamBtn = document.getElementById('nav-hamburger');
        const navOverlay = document.getElementById('nav-overlay');
        const navClose = document.getElementById('nav-close');
        if (hamBtn && navOverlay) {
            hamBtn.addEventListener('click', () => navOverlay.classList.add('active'));
            navClose.addEventListener('click', () => navOverlay.classList.remove('active'));
            navOverlay.querySelectorAll('a').forEach(a => {
                a.addEventListener('click', () => navOverlay.classList.remove('active'));
            });
        }
'''

# Also add smoother transitions for HUD panels
hud_transition_css = '''
        .hud-left, .hud-right {
            transition: transform 0.3s ease, opacity 0.3s ease;
        }
        .hud-left.collapsed { transform: translateX(-120%); opacity: 0; }
        .hud-right.collapsed { transform: translateX(120%); opacity: 0; }
'''

pages = [
    'docs/pages/mapper-3d.html',
    'docs/pages/interception-mission.html',
    'docs/pages/satellite-digital-twin.html',
    'docs/pages/hypersonic.html',
    'docs/pages/opa-analysis.html',
    'docs/pages/foundry-cleanroom.html',
]

for page in pages:
    if not os.path.exists(page):
        continue
    
    with open(page, 'r') as f:
        content = f.read()
    
    original = content
    
    # 1. Inject hamburger CSS
    if 'nav-hamburger' not in content:
        content = content.replace('</style>', hamburger_css + hud_transition_css + '\n    </style>')
    
    # 2. Inject hamburger HTML after <body>
    if 'nav-overlay' not in content:
        content = content.replace('<body>', '<body>\n' + hamburger_html)
    
    # 3. Inject hamburger JS
    if 'nav-hamburger' not in content or 'hamBtn' not in content:
        # Find the UI JS section or last script
        last_script = content.rfind('</script>')
        if last_script > 0:
            content = content[:last_script] + hamburger_js + '\n    ' + content[last_script:]
    
    if content != original:
        with open(page, 'w') as f:
            f.write(content)
        print(f"✅ {os.path.basename(page)} - Hamburger nav added")
    else:
        print(f"⏭️ {os.path.basename(page)} - no changes")

print("\n🎉 Hamburger navigation and smooth HUD transitions added!")
