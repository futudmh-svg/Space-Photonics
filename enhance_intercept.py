#!/usr/bin/env python3
"""Enhance interception-mission.html with future trajectory in animate loop and velocity vectors."""

with open('docs/pages/interception-mission.html', 'r') as f:
    content = f.read()

# 1. Add future path updates to animate() function
old_animate = """            updateSats(dt);
            const enemyPos = updateEnemy(dt);
            const intPos = updateInterceptor(dt);
            updateBeams(enemyPos, intPos);
            drawCameraFeed();"""

new_animate = """            updateSats(dt);
            const enemyPos = updateEnemy(dt);
            const intPos = updateInterceptor(dt);

            // Future trajectory prediction
            if (enemyPos) {
                const eState = getEnemyState(simTime);
                const eVel = new THREE.Vector3(
                    Math.cos(eState.lon) * Math.cos(eState.lat),
                    Math.sin(eState.lat),
                    Math.sin(eState.lon) * Math.cos(eState.lat)
                ).normalize().multiplyScalar(eState.mach * 343);
                updateFuturePath(enemyFuture, enemyPos, eVel, 80);
                enemyFuture.line.computeLineDistances();
            }
            if (intPos) {
                const iState = getIntState(simTime);
                const enemyNow = getEnemyState(simTime).pos;
                const iVel = enemyNow.clone().sub(intPos).normalize().multiplyScalar(iState.mach * 343);
                updateFuturePath(intFuture, intPos, iVel, 60);
                intFuture.line.computeLineDistances();
            }

            updateBeams(enemyPos, intPos);
            drawCameraFeed();"""

content = content.replace(old_animate, new_animate)

# 2. Add velocity arrow helpers for enemy and interceptor
old_enemy_body = """// Body
        const hBodyGeo = new THREE.ConeGeometry(0.1, 0.5, 8);"""
new_enemy_body = """// Velocity arrow
        const enemyVelArrow = new THREE.ArrowHelper(
            new THREE.Vector3(0,0,1), new THREE.Vector3(0,0,0), 1.5, 0xe63946, 0.4, 0.25
        );
        enemyGroup.add(enemyVelArrow);

        // Body
        const hBodyGeo = new THREE.ConeGeometry(0.1, 0.5, 8);"""
content = content.replace(old_enemy_body, new_enemy_body)

old_int_body = """const iBody = new THREE.Mesh(
            new THREE.CylinderGeometry(0.06, 0.08, 0.5, 8),"""
new_int_body = """// Velocity arrow
        const intVelArrow = new THREE.ArrowHelper(
            new THREE.Vector3(0,0,1), new THREE.Vector3(0,0,0), 1.5, 0x2a9d8f, 0.4, 0.25
        );
        intGroup.add(intVelArrow);

        const iBody = new THREE.Mesh(
            new THREE.CylinderGeometry(0.06, 0.08, 0.5, 8),"""
content = content.replace(old_int_body, new_int_body)

# 3. Update velocity arrows in updateEnemy and updateInterceptor
old_enemy_lookat = "enemyGroup.lookAt(targetPos);"
new_enemy_lookat = """enemyGroup.lookAt(targetPos);

            // Update velocity arrow
            const eDir = targetPos.clone().sub(enemyPos).normalize();
            enemyVelArrow.setDirection(eDir);
            enemyVelArrow.setLength(Math.max(0.5, state.mach * 0.15), 0.4, 0.25);"""
content = content.replace(old_enemy_lookat, new_enemy_lookat)

old_int_lookat = "intGroup.lookAt(getEnemyState(simTime).pos);"
new_int_lookat = """intGroup.lookAt(getEnemyState(simTime).pos);

            // Update velocity arrow
            const iDir = getEnemyState(simTime).pos.clone().sub(intPos).normalize();
            intVelArrow.setDirection(iDir);
            intVelArrow.setLength(Math.max(0.5, state.mach * 0.1), 0.4, 0.25);"""
content = content.replace(old_int_lookat, new_int_lookat)

# 4. Add closing velocity and miss distance to HUD
old_int_pkill = "document.getElementById('int-pkill').textContent = pkill.toFixed(0) + '%';"
new_int_pkill = """document.getElementById('int-pkill').textContent = pkill.toFixed(0) + '%';
            const missDist = range * Math.sin(0.01); // approximate
            document.getElementById('int-miss').textContent = missDist < 0.1 ? '< 100 m' : missDist.toFixed(1) + ' km';"""
content = content.replace(old_int_pkill, new_int_pkill)

# 5. Add miss distance element to HTML if not present
if 'int-miss' not in content:
    old_int_hud = "<div class=\"hud-row\"><span class=\"hud-label\">P_kill</span><span class=\"hud-value ok\" id=\"int-pkill\">92%</span></div>"
    new_int_hud = """<div class="hud-row"><span class="hud-label">P_kill</span><span class="hud-value ok" id="int-pkill">92%</span></div>
        <div class="hud-row"><span class="hud-label">Est. Miss Dist</span><span class="hud-value" id="int-miss">&lt; 100 m</span></div>"""
    content = content.replace(old_int_hud, new_int_hud)

with open('docs/pages/interception-mission.html', 'w') as f:
    f.write(content)

print("✅ interception-mission.html enhanced with:")
print("   - Future trajectory prediction in animate loop")
print("   - Velocity vector arrows on both vehicles")
print("   - Estimated miss distance in HUD")
