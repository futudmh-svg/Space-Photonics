#!/usr/bin/env python3
"""
Enhance mapper-3d.html with:
1. Additional physics variables in HUD (Reynolds, Knudsen, hoop stress, skin depth)
2. Better rocket swarm visibility (labels, brighter colors, larger flames)
3. Trajectory markers with velocity vectors
"""

import re

with open('docs/pages/mapper-3d.html', 'r') as f:
    content = f.read()

# 1. Add extra physics rows to HUD - find the Thermal section and add Aerodynamics section before it
thermal_section = '''        <div class="hud-section">
            <div class="hud-section-title">🌡️ Thermal</div>'''

aero_section = '''        <div class="hud-section">
            <div class="hud-section-title">🌀 Aerodynamics</div>
            <div class="hud-row"><span class="hud-label">Reynolds Number</span><span class="hud-value" id="hud-re">1.2e7</span></div>
            <div class="hud-row"><span class="hud-label">Knudsen Number</span><span class="hud-value" id="hud-kn">0.002</span></div>
            <div class="hud-row"><span class="hud-label">Hoop Stress</span><span class="hud-value" id="hud-hoop">0.85 MPa</span></div>
            <div class="hud-row"><span class="hud-label">Skin Depth</span><span class="hud-value" id="hud-skin">0.18 mm</span></div>
        </div>

        <div class="hud-section">
            <div class="hud-section-title">🌡️ Thermal</div>'''

content = content.replace(thermal_section, aero_section)

# 2. Enhance updateHUD function to include new physics variables
# Find the existing enemy-plasma line and add after it
old_enemy_doppler = "document.getElementById('enemy-doppler').textContent = '+' + (enemy.mach * 0.214).toFixed(2) + ' GHz';"
new_enemy_doppler = """document.getElementById('enemy-doppler').textContent = '+' + (enemy.mach * 0.214).toFixed(2) + ' GHz';
            document.getElementById('hud-re').textContent = ePhys.Re.toExponential(1);
            document.getElementById('hud-kn').textContent = ePhys.Kn.toFixed(3);
            document.getElementById('hud-hoop').textContent = ePhys.hoop.toFixed(2) + ' MPa';
            document.getElementById('hud-skin').textContent = (ePhys.skinDepth * 1000).toFixed(2) + ' mm';"""

content = content.replace(old_enemy_doppler, new_enemy_doppler)

# 3. Enhance rocket visibility - make flames brighter and add labels
# Find rocket flame material and enhance
old_flame = """const flameMat = new THREE.MeshBasicMaterial({
                color: 0xff4400, transparent: true, opacity: 0.8, blending: THREE.AdditiveBlending
            });"""
new_flame = """const flameMat = new THREE.MeshBasicMaterial({
                color: 0xff6600, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending
            });"""
content = content.replace(old_flame, new_flame)

# 4. Add rocket label sprites
old_rocket_return = """return {
                group, body, nose, flame, flame2, trail, trailPos,"""
new_rocket_return = """// Label sprite
            const labelCanvas = document.createElement('canvas');
            labelCanvas.width = 128; labelCanvas.height = 32;
            const lctx = labelCanvas.getContext('2d');
            lctx.fillStyle = 'rgba(5,8,17,0.85)';
            lctx.fillRect(0, 0, 128, 32);
            lctx.strokeStyle = '#ffd166'; lctx.lineWidth = 1;
            lctx.strokeRect(0, 0, 128, 32);
            lctx.fillStyle = '#ffd166';
            lctx.font = 'bold 14px monospace';
            lctx.textAlign = 'center';
            const labelText = config.type === 'heavy' ? 'HEAVY-' + (index+1) : config.type === 'medium' ? 'MED-' + (index-1) : 'SS-' + (index-5);
            lctx.fillText(labelText, 64, 22);
            const labelTex = new THREE.CanvasTexture(labelCanvas);
            const labelSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: labelTex, transparent: true }));
            labelSprite.scale.set(2, 0.5, 1);
            labelSprite.position.y = 1.2 * s;
            group.add(labelSprite);

            return {
                group, body, nose, flame, flame2, trail, trailPos, labelSprite,"""
content = content.replace(old_rocket_return, new_rocket_return)

# 5. Make rocket trails more visible
old_trail_mat = """const trailMat = new THREE.PointsMaterial({
                color: 0xff6600, size: 0.2 * s, transparent: true, opacity: 0.6,
                blending: THREE.AdditiveBlending, depthWrite: false
            });"""
new_trail_mat = """const trailMat = new THREE.PointsMaterial({
                color: 0xffaa00, size: 0.35 * s, transparent: true, opacity: 0.85,
                blending: THREE.AdditiveBlending, depthWrite: false
            });"""
content = content.replace(old_trail_mat, new_trail_mat)

# 6. Add velocity vector arrows for vehicles
# Find where enemyVehicle and friendlyVehicle are created and add arrow helpers
old_enemy_create = "const enemyVehicle = createHypersonicVehicle(ENEMY_CONFIG);"
new_enemy_create = """const enemyVehicle = createHypersonicVehicle(ENEMY_CONFIG);
        // Velocity vector arrow
        const enemyArrow = new THREE.ArrowHelper(
            new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 0), 2, 0xe63946, 0.5, 0.3
        );
        enemyVehicle.group.add(enemyArrow);
        enemyVehicle.velocityArrow = enemyArrow;"""
content = content.replace(old_enemy_create, new_enemy_create)

old_friendly_create = "const friendlyVehicle = createHypersonicVehicle(FRIENDLY_CONFIG);"
new_friendly_create = """const friendlyVehicle = createHypersonicVehicle(FRIENDLY_CONFIG);
        const friendlyArrow = new THREE.ArrowHelper(
            new THREE.Vector3(1, 0, 0), new THREE.Vector3(0, 0, 0), 2, 0x2a9d8f, 0.5, 0.3
        );
        friendlyVehicle.group.add(friendlyArrow);
        friendlyVehicle.velocityArrow = friendlyArrow;"""
content = content.replace(old_friendly_create, new_friendly_create)

# 7. Update velocity arrows in animate loop
old_enemy_lookat = """enemyVehicle.group.lookAt(
                enemyState.pos.x + Math.cos(enemyState.heading) * 100,
                enemyState.pos.y,
                enemyState.pos.z + Math.sin(enemyState.heading) * 100
            );"""
new_enemy_lookat = """enemyVehicle.group.lookAt(
                enemyState.pos.x + Math.cos(enemyState.heading) * 100,
                enemyState.pos.y,
                enemyState.pos.z + Math.sin(enemyState.heading) * 100
            );
            // Update velocity arrow
            const eVelDir = new THREE.Vector3(
                Math.cos(enemyState.heading * Math.PI / 180), 0, Math.sin(enemyState.heading * Math.PI / 180)
            ).normalize();
            enemyVehicle.velocityArrow.setDirection(eVelDir);
            enemyVehicle.velocityArrow.setLength(Math.max(1, enemyState.mach * 0.2), 0.5, 0.3);"""
content = content.replace(old_enemy_lookat, new_enemy_lookat)

# 8. Make future path more visible with dashed material
old_future_path = """// Projected future paths
        const enemyFuture = createTrajectoryCurve(0xe63946);
        const friendlyFuture = createTrajectoryCurve(0x2a9d8f);
        enemyFuture.line.material.opacity = 0.2;
        friendlyFuture.line.material.opacity = 0.2;
        enemyFuture.line.material.linewidth = 1;
        friendlyFuture.line.material.linewidth = 1;"""
new_future_path = """// Projected future paths (dashed)
        function createDashedFuturePath(color) {
            const pts = [];
            for (let i = 0; i < 200; i++) pts.push(new THREE.Vector3(0,0,0));
            const geo = new THREE.BufferGeometry().setFromPoints(pts);
            const mat = new THREE.LineDashedMaterial({
                color: color, transparent: true, opacity: 0.35,
                dashSize: 0.4, gapSize: 0.2, scale: 1
            });
            return { line: new THREE.Line(geo, mat), pts };
        }
        const enemyFuture = createDashedFuturePath(0xe63946);
        const friendlyFuture = createDashedFuturePath(0x2a9d8f);"""
content = content.replace(old_future_path, new_future_path)

# 9. Fix updateFuturePath for dashed lines
old_update_future = """function updateFuturePath(future, pos, heading, mach, steps) {
            const pts = [];
            for (let i = 0; i < steps; i++) {
                const dist = i * mach * 343 * 0.5;
                const lat = Math.asin(pos.y / pos.length()) + Math.cos(heading) * dist / EARTH_R;
                const lon = Math.atan2(pos.z, pos.x) + Math.sin(heading) * dist / EARTH_R;
                const r = EARTH_R + pos.length() - EARTH_R;
                pts.push(new THREE.Vector3(
                    r * Math.cos(lat) * Math.cos(lon),
                    r * Math.sin(lat),
                    r * Math.cos(lat) * Math.sin(lon)
                ));
            }
            future.line.geometry.setFromPoints(pts);
        }"""
new_update_future = """function updateFuturePath(future, pos, heading, mach, steps) {
            const pts = [];
            for (let i = 0; i < steps; i++) {
                const dist = i * mach * 343 * 0.5;
                const lat = Math.asin(pos.y / pos.length()) + Math.cos(heading) * dist / EARTH_R;
                const lon = Math.atan2(pos.z, pos.x) + Math.sin(heading) * dist / EARTH_R;
                const r = EARTH_R + pos.length() - EARTH_R;
                pts.push(new THREE.Vector3(
                    r * Math.cos(lat) * Math.cos(lon),
                    r * Math.sin(lat),
                    r * Math.cos(lat) * Math.sin(lon)
                ));
            }
            future.line.geometry.setFromPoints(pts);
            future.line.computeLineDistances();
        }"""
content = content.replace(old_update_future, new_update_future)

with open('docs/pages/mapper-3d.html', 'w') as f:
    f.write(content)

print("✅ mapper-3d.html enhanced with:")
print("   - Aerodynamics HUD (Re, Kn, hoop stress, skin depth)")
print("   - Velocity vector arrows on vehicles")
print("   - Dashed future trajectory paths")
print("   - Brighter rocket flames and labels")
print("   - Enhanced rocket trails")
