#!/usr/bin/env python3
"""
Fix UI/UX issues across all Three.js pages:
1. Responsive navigation (hamburger on mobile)
2. Collapsible HUD panels
3. Better z-index and spacing
4. Mobile-optimized layouts
5. Fullscreen toggle
"""

import os, re

# Shared responsive CSS injection
responsive_css = '''
        /* ─── Responsive & Mobile ─── */
        @media (max-width: 900px) {
            nav { flex-wrap: nowrap; overflow-x: auto; justify-content: flex-start; padding: 4px; gap: 2px; }
            nav a { font-size: 0.65em; padding: 4px 6px; flex-shrink: 0; }
            .hud-left, .hud-right { width: 180px; font-size: 0.65em; max-height: calc(100vh - 220px); }
            .hud-left { left: 4px; top: 55px; }
            .hud-right { right: 4px; top: 55px; }
            .scenario-controls { top: 55px; }
            .scenario-btn { padding: 5px 8px; font-size: 0.7em; }
            .time-controls { padding: 6px 8px; gap: 4px; }
            .minimap-container { display: none; }
            .cam-indicator { display: none; }
            .camera-feed { width: 240px; height: 150px; }
            #cam-canvas { height: 80px !important; }
        }
        @media (max-width: 600px) {
            .hud-left, .hud-right { width: 150px; font-size: 0.6em; padding: 6px; }
            .hud-bottom-left, .hud-bottom-right { display: none; }
            .camera-feed { width: 200px; height: 120px; right: 4px; left: auto; transform: none; bottom: 50px; }
            .time-controls { left: 4px; transform: none; }
        }
        
        /* Collapsible HUD */
        .hud-toggle {
            position: fixed; top: 55px; z-index: 150;
            background: rgba(5,8,17,0.9); border: 1px solid #00d4aa;
            color: #00d4aa; padding: 4px 8px; border-radius: 4px;
            cursor: pointer; font-size: 0.7em; display: none;
        }
        @media (max-width: 900px) {
            .hud-toggle { display: block; }
            .hud-left.collapsed, .hud-right.collapsed { display: none; }
        }
        #toggle-left { left: 4px; }
        #toggle-right { right: 4px; }
        
        /* Fullscreen mode */
        body.fullscreen nav,
        body.fullscreen .hud-left,
        body.fullscreen .hud-right,
        body.fullscreen .scenario-controls,
        body.fullscreen .time-controls,
        body.fullscreen .hud-bottom-left,
        body.fullscreen .hud-bottom-right,
        body.fullscreen .camera-feed,
        body.fullscreen .minimap-container,
        body.fullscreen .cam-indicator,
        body.fullscreen .hud-toggle {
            display: none !important;
        }
        #fs-toggle {
            position: fixed; top: 55px; right: 50%; transform: translateX(50%);
            z-index: 150; background: rgba(5,8,17,0.9); border: 1px solid #00d4aa;
            color: #00d4aa; padding: 4px 10px; border-radius: 4px;
            cursor: pointer; font-size: 0.7em;
        }
        body.fullscreen #fs-toggle { display: block !important; top: 8px; right: 8px; transform: none; }
'''

# Shared JS for UI toggles
ui_js = '''
        // HUD collapse toggles
        const leftHud = document.querySelector('.hud-left');
        const rightHud = document.querySelector('.hud-right');
        if (leftHud) {
            const btn = document.createElement('button');
            btn.id = 'toggle-left'; btn.className = 'hud-toggle';
            btn.textContent = '◀ HUD';
            btn.onclick = () => { leftHud.classList.toggle('collapsed'); btn.textContent = leftHud.classList.contains('collapsed') ? '▶ HUD' : '◀ HUD'; };
            document.body.appendChild(btn);
        }
        if (rightHud) {
            const btn = document.createElement('button');
            btn.id = 'toggle-right'; btn.className = 'hud-toggle';
            btn.textContent = 'HUD ▶';
            btn.onclick = () => { rightHud.classList.toggle('collapsed'); btn.textContent = rightHud.classList.contains('collapsed') ? 'HUD ◀' : 'HUD ▶'; };
            document.body.appendChild(btn);
        }
        // Fullscreen toggle
        const fsBtn = document.createElement('button');
        fsBtn.id = 'fs-toggle'; fsBtn.textContent = '⛶ Fullscreen';
        fsBtn.onclick = () => {
            document.body.classList.toggle('fullscreen');
            fsBtn.textContent = document.body.classList.contains('fullscreen') ? '⛶ Exit' : '⛶ Fullscreen';
        };
        document.body.appendChild(fsBtn);
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
        print(f"⚠️ Skip {page} (not found)")
        continue
    
    with open(page, 'r') as f:
        content = f.read()
    
    original = content
    
    # 1. Inject responsive CSS before </style>
    if 'Responsive & Mobile' not in content:
        content = content.replace('</style>', responsive_css + '\n    </style>')
    
    # 2. Inject UI JS at end of module script or before </script> if module
    if 'fullscreen nav' not in content:
        # Find the last </script> that contains module code
        last_script_end = content.rfind('</script>')
        if last_script_end > 0:
            content = content[:last_script_end] + ui_js + '\n    ' + content[last_script_end:]
    
    if content != original:
        with open(page, 'w') as f:
            f.write(content)
        print(f"✅ {page} - UI optimized")
    else:
        print(f"⏭️ {page} - no changes needed")

print("\n🎉 All pages optimized for mobile and responsive viewing!")
