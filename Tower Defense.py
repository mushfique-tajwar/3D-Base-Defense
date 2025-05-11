# Made by

# 22301068 - Mushfique Tajwar
# 22301130 - Aryan Rayeen Rahman
# 22301327 - Md. Obaidullah Ahrar

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# Setup
GRID_LENGTH = 1500
region = 600
castle_region = 250
# Camera
camera_position, camera_angle = (0, 600, 600), 0
camera_distance, camera_height = 600, 550
camera_min_height, camera_max_height = 400, 1400
# Flags
game_end, first_person_view, cheat, v_enable = False, False, False, False
round_pause = False
round_choice_made = False
# Player
player_position, gun_rotation = [0, 0, 0], 180
player_speed, player_rotation, player_health, player_max_health, player_score = 10, 5, 100, 100, 0
# Gun
shots, misses, max_miss, gun_position = [], 0, 50, [30, 15, 80]
# Target
target_pulse, target_pulse_t = 1.0, 0
# Enemy shots
enemy_shots = []
enemy_shot_cooldown = 300
enemy_shot_timer = {}
enemy_shot_damage = 1

# Tower shots
tower_shots = []
tower_shot_cooldown = 200
tower_shot_timers = {}
tower_shot_range = 600
tower_shot_damage = 3

current_round = 1
castle_radius = 60
enemies_killed = 0
kills_to_advance = 10

towers = []
tower_placement_mode = False
placement_marker_position = [400, 400]

GLUT_BITMAP_HELVETICA_18 = GLUT_BITMAP_HELVETICA_18
targets, target_speed, target_number = [], 0.025, 5
enemy_count_per_round = [5, 7, 9, 11, 13, 15]

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18, color=(1, 1, 1)):
    glColor3f(color[0], color[1], color[2])
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 650)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(font, ord(character))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_shapes():
    arena()
    castle()
    for tx, ty in towers:
        glPushMatrix()
        glTranslatef(tx, ty, 10)
        # Base Cylinder Tower
        glColor3f(0.5, 0.5, 0.5)
        gluCylinder(gluNewQuadric(), 40, 45, 180, 20, 20)
        # Top Battlements
        glTranslatef(0, 0, 180)
        for i in range(8):
            angle = i * 45
            x = 50 * math.cos(math.radians(angle))
            y = 50 * math.sin(math.radians(angle))
            glPushMatrix()
            glTranslatef(x, y, 0)
            glRotatef(angle, 0, 0, 1)
            glColor3f(0.4, 0.4, 0.4)
            glScalef(1, 1, 1.5)
            glutSolidCube(15)
            glPopMatrix()
        # Flagpole
        glColor3f(0.6, 0.3, 0.1)
        gluCylinder(gluNewQuadric(), 1.5, 1.5, 40, 10, 10)
        # Flag
        glTranslatef(0, 0, 40)
        glColor3f(1, 0, 0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(20, 8, 0)
        glVertex3f(0, 16, 0)
        glEnd()
        glPopMatrix()
    if not game_end:
        for t in targets:
            enemies(*t)
        for s in shots:
            bullets(s[0], s[1], s[2])
        for es in enemy_shots:
            enemy_bullet(es[0], es[1], es[2])
        for ts in tower_shots:
            tower_bullet(ts[0], ts[1], ts[2])

def arena():
    # Draw arena floor
    glBegin(GL_QUADS)
    for i in range(-GRID_LENGTH, GRID_LENGTH + 1, 100):
        for j in range(-GRID_LENGTH, GRID_LENGTH + 1, 100):
            if (i + j) % 200 == 0:
                glColor3f(0, 0.2, 0)
            else:
                glColor3f(0, 0.3, 0)
            glVertex3f(i, j, 0)
            glVertex3f(i + 100, j, 0)
            glVertex3f(i + 100, j + 100, 0)
            glVertex3f(i, j + 100, 0)
    glEnd()
    glBegin(GL_QUADS)
    for i in range(-region, region + 1, 100):
        for j in range(-region, region + 1, 100):
            if (i + j) % 200 == 0:
                glColor3f(0, 0.4, 0)
            else:
                glColor3f(0, 0.5, 0)
            glVertex3f(i, j, 2)
            glVertex3f(i + 100, j, 2)
            glVertex3f(i + 100, j + 100, 2)
            glVertex3f(i, j + 100, 2)
    glEnd()
    glBegin(GL_QUADS)
    for i in range(-castle_region, castle_region, 100):
        for j in range(-castle_region, castle_region, 100):
            if (i + j) % 200 == 0:
                glColor3f(0.8, 0.8, 0.8)
            else:
                glColor3f(1, 1, 1)
            glVertex3f(i, j, 9)
            glVertex3f(i + 100, j, 9)
            glVertex3f(i + 100, j + 100, 9)
            glVertex3f(i, j + 100, 9)
    glEnd()
    # Boundary
    glBegin(GL_QUADS)
    glColor3f(0, 0, 0)

    glVertex3f(-region, -region, 0)
    glVertex3f(-region, region + 100, 0)
    glVertex3f(-region, region + 100, 30)
    glVertex3f(-region, -region, 30)

    glVertex3f(region + 100, -region, 0)
    glVertex3f(region + 100, region + 100, 0)
    glVertex3f(region + 100, region + 100, 30)
    glVertex3f(region + 100, -region, 30)

    glVertex3f(-region, region + 100, 0)
    glVertex3f(region + 100, region + 100, 0)
    glVertex3f(region + 100, region + 100, 30)
    glVertex3f(-region, region + 100, 30)

    glVertex3f(-region, -region, 0)
    glVertex3f(region + 100, -region, 0)
    glVertex3f(region + 100, -region, 30)
    glVertex3f(-region, -region, 30)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.2, 0.2)

    # Walls
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH + 100, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH + 100, 100)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 100)

    glVertex3f(GRID_LENGTH + 100, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH + 100, GRID_LENGTH + 100, 0)
    glVertex3f(GRID_LENGTH + 100, GRID_LENGTH + 100, 100)
    glVertex3f(GRID_LENGTH + 100, -GRID_LENGTH, 100)

    glVertex3f(-GRID_LENGTH, GRID_LENGTH + 100, 0)
    glVertex3f(GRID_LENGTH + 100, GRID_LENGTH + 100, 0)
    glVertex3f(GRID_LENGTH + 100, GRID_LENGTH + 100, 100)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH + 100, 100)

    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH + 100, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH + 100, -GRID_LENGTH, 100)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 100)
    glEnd()
    rng = random.Random(42)
    tree_count = 70
    for _ in range(tree_count):
        x = rng.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
        y = rng.randint(-GRID_LENGTH + 200, GRID_LENGTH - 200)
        if math.sqrt(x**2 + y**2) >= 500:
            glPushMatrix()
            glTranslatef(x, y, 0)
            glColor3f(0.4, 0.2, 0.1)
            gluCylinder(gluNewQuadric(), 12, 12, 70, 10, 10)
            glTranslatef(0, 0, 70)
            glColor3f(0.0, 0.6, 0.0)
            gluSphere(gluNewQuadric(), 40, 15, 15)
            glPopMatrix()

def castle():
    glPushMatrix()
    glColor3f(0.7, 0.7, 0.7)
    for dx, dy in [(-60, -60), (60, -60), (-60, 60), (60, 60)]:
        glPushMatrix()
        glTranslatef(dx, dy, 0)
        glScalef(1, 1, 2)
        glutSolidCube(100)
        glPopMatrix()
    glPopMatrix()
    glColor3f(0.6, 0.6, 0.6)
    for dx, dy in [(-100, 0), (100, 0), (0, -100), (0, 100)]:
        glPushMatrix()
        glTranslatef(dx, dy, 50)
        glScalef(1.2, 1.2, 2.2)
        glutSolidCube(60)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(dx, dy, 120)
        for i in range(8):
            angle = i * 45
            x = 35 * math.cos(math.radians(angle))
            y = 35 * math.sin(math.radians(angle))
            glPushMatrix()
            glTranslatef(x, y, 0)
            glColor3f(0.5, 0.5, 0.5)
            glutSolidCube(12)
            glPopMatrix()
        glPopMatrix()
    glColor3f(1, 0, 0)  # Red flags
    for dx, dy in [(-100, 0), (100, 0), (0, -100), (0, 100)]:
        glPushMatrix()
        glTranslatef(dx, dy, 150)
        # Flag pole
        glColor3f(0.6, 0.3, 0.1)
        gluCylinder(gluNewQuadric(), 1.5, 1.5, 40, 10, 10)
        # Flag
        glTranslatef(0, 0, 40)
        glColor3f(1, 0, 0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0, 0, 0)
        glVertex3f(25, 10, 0)
        glVertex3f(0, 20, 0)
        glEnd()
        glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0, 0)
    glColor3f(0.4, 0.4, 0.9)
    gluCylinder(gluNewQuadric(), 40, 50, 200, 20, 20)
    glTranslatef(0, 0, 200)
    for i in range(12):
        angle = i * 30
        x = 50 * math.cos(math.radians(angle))
        y = 50 * math.sin(math.radians(angle))
        glPushMatrix()
        glTranslatef(x, y, 0)
        glColor3f(0.5, 0.5, 0.6)
        glutSolidCube(12)
        glPopMatrix()
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0,0,200)
    glRotatef(gun_rotation, 0, 0, 1)
    # Legs
    glTranslatef(0, 0, 0)
    glColor3f(0.1, 0.1, 0.7)
    gluCylinder(gluNewQuadric(), 6, 12, 45, 10, 10)
    glTranslatef(30, 0, 0)
    glColor3f(0.1, 0.1, 0.7)
    gluCylinder(gluNewQuadric(), 6, 12, 45, 10, 10)
    # Body
    glTranslatef(-15, 0, 70)
    glColor3f(0.7, 0.7, 0)
    glutSolidCube(40)
    # Head
    glTranslatef(0, 0, 40)
    glColor3f(0.95, 0.85, 0.75)
    gluSphere(gluNewQuadric(), 20, 12, 12)
    # Arms
    glTranslatef(20, -60, -30)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0.95, 0.85, 0.75)
    gluCylinder(gluNewQuadric(), 4, 8, 50, 10, 10)
    glRotatef(90, 1, 0, 0)
    glTranslatef(-45, 60, -40)
    glRotatef(0, 1, 0, 0)
    glColor3f(0.95, 0.85, 0.75)
    gluCylinder(gluNewQuadric(), 4, 8, 50, 10, 10)
    glPopMatrix()

def spawn_tower():
    while True:
        x = random.randint(-region + 100, region - 100)
        y = random.randint(-region + 100, region - 100)
        if math.sqrt(x**2 + y**2) > 200:  # Avoid center
            return (x, y)

def enemies(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z + 35)
    if not round_pause:
        glScalef(target_pulse, target_pulse, target_pulse)
    # Lower Body (Upside-down Cone)
    glColor3f(0, 0, 1)  # Blue color for the lower body
    glPushMatrix()
    glTranslatef(0,0,35)
    glRotatef(180, 1, 0, 0)  # Rotate the cone upside down
    glutSolidCone(25, 70, 16, 16)  # Base radius = 35, height = 50
    glPopMatrix()
    # Head
    glTranslatef(0, 0, 50)
    glColor3f(0, 0, 0)  # Black color for the head
    gluSphere(gluNewQuadric(), 15, 12, 12)
    # Hat
    glPushMatrix()
    glColor3f(0.5, 0, 0)  # Red color for the hat
    glTranslatef(0, 0, 20)
    glutSolidCone(12, 40, 16, 16)  # Base radius = 12, height = 40
    glPopMatrix()
    glPopMatrix()

def bullets(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)
    glColor3f(1, 0.5, 0)
    glutSolidCube(8)
    glPopMatrix()

def tower_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)
    glColor3f(0, 0.7, 1)  # Blue color for tower bullets
    glutSolidCone(4, 12, 8, 8)  # Cone shape for tower bullets
    glPopMatrix()

def enemy_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)
    glColor3f(1, 0, 0)  # Red color for enemy bullets
    glutSolidSphere(5, 8, 8)  # Sphere for enemy bullets
    glPopMatrix()

def shoot():
    global shots
    if first_person_view:
        ang = math.radians(gun_rotation + 45)
        x = player_position[0] + (gun_position[0] + 5) * \
            math.sin(ang) - gun_position[1] * math.cos(ang)
        y = player_position[1] - (gun_position[0] + 5) * \
            math.cos(ang) - gun_position[1] * math.sin(ang)
        z = player_position[2] + gun_position[2]
        shot = [x, y, z, gun_rotation]
    else:
        ang = math.radians(gun_rotation - 90)
        off_x = gun_position[0] * \
            math.cos(ang) - gun_position[1] * math.sin(ang)
        off_y = gun_position[0] * \
            math.sin(ang) + gun_position[1] * math.cos(ang)
        x = player_position[0] + off_x
        y = player_position[1] + off_y
        z = player_position[2] + gun_position[2]
        shot = [x, y, z, gun_rotation]
    shots.append(shot)

def gun_shot_check():
    global shots, misses, targets, game_end
    if round_pause:
        return
    to_remove = []
    for s in shots:
        ang = math.radians(s[3] - 90)
        s[0] += 2 * math.cos(ang)
        s[1] += 2 * math.sin(ang)
        if (s[0] > region + 100 or s[0] < -region or
                s[1] > region + 100 or s[1] < -region):
            to_remove.append(s)
            if not cheat:
                misses += 1
    for s in to_remove:
        if s in shots:
            shots.remove(s)
    if misses >= max_miss and not cheat:
        game_end = True

def enemy_shoot(x, y, z):
    global enemy_shots
    dx = player_position[0] - x
    dy = player_position[1] - y
    ang = math.atan2(dy, dx)
    ang += random.uniform(-0.1, 0.1)
    enemy_shots.append([x, y, z + 70, ang])

def update_enemies():
    global targets, player_health, game_end, target_speed, enemy_shot_timer
    if round_pause:
        return
    for t in targets:
        enemy_id = id(t)
        if enemy_id not in enemy_shot_timer:
            enemy_shot_timer[enemy_id] = random.randint(
                60, enemy_shot_cooldown)
    for t in targets[:]:
        dx = player_position[0] - t[0]
        dy = player_position[1] - t[1]
        dist = math.sqrt(dx*dx + dy*dy)
        enemy_id = id(t)
        if enemy_id in enemy_shot_timer:
            enemy_shot_timer[enemy_id] -= 1
            if enemy_shot_timer[enemy_id] <= 0 and not cheat:
                enemy_shoot(t[0], t[1], t[2])
                enemy_shot_timer[enemy_id] = enemy_shot_cooldown + \
                    random.randint(-30, 30)
        if dist < 50:
            if not cheat:
                player_health -= 1
                if player_health <= 0:
                    game_end = True
                    targets.clear()
                    shots.clear()
                    enemy_shots.clear()
                    break
            if t in targets:
                targets.remove(t)
                if enemy_id in enemy_shot_timer:
                    del enemy_shot_timer[enemy_id]
            spawn_enemies(1)
        else:
            ang = math.atan2(dy, dx)
            t[0] += target_speed * math.cos(ang)
            t[1] += target_speed * math.sin(ang)
    timer_keys = list(enemy_shot_timer.keys())
    for enemy_id in timer_keys:
        if not any(id(t) == enemy_id for t in targets):
            del enemy_shot_timer[enemy_id]
    if not targets:
        next_round()

def detect_target_hits():
    global shots, targets, player_score, enemies_killed
    if round_pause:
        return
    for s in shots[:]:
        s_x, s_y = s[0], s[1]
        for t in targets[:]:
            t_x, t_y = t[0], t[1]
            dx, dy = s_x - t_x, s_y - t_y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist <= 70:
                player_score += 1
                enemies_killed += 1
                if s in shots:
                    shots.remove(s)
                if t in targets:
                    targets.remove(t)
                max_enemies = (
                    enemy_count_per_round[current_round-1]
                    if current_round <= len(enemy_count_per_round)
                    else enemy_count_per_round[-1] + 2 * (current_round - len(enemy_count_per_round))
                )
                if enemies_killed >= kills_to_advance:
                    next_round()
                elif len(targets) < max_enemies:
                    spawn_enemies(1)
                break

def tower_shoot(tower_idx, tx, ty):
    global tower_shots, targets
    closest_enemy = None
    min_dist = tower_shot_range
    for t in targets:
        dx = tx - t[0]
        dy = ty - t[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < min_dist:
            min_dist = dist
            closest_enemy = t
    if closest_enemy:
        ex, ey, _ = closest_enemy
        dx = ex - tx
        dy = ey - ty
        ang = math.atan2(dy, dx)
        ang += random.uniform(-0.05, 0.05)
        tower_shots.append([tx, ty, 160, ang])
        return True
    return False

def update_towers():
    global tower_shot_timers, towers
    if round_pause:
        return
    for i, (tx, ty) in enumerate(towers):
        if i in tower_shot_timers:
            tower_shot_timers[i] -= 1
            if tower_shot_timers[i] <= 0:
                if tower_shoot(i, tx, ty):
                    tower_shot_timers[i] = tower_shot_cooldown
                else:
                    tower_shot_timers[i] = 60
        else:
            tower_shot_timers[i] = random.randint(60, tower_shot_cooldown)

def update_tower_shots():
    global tower_shots, targets, player_score, enemies_killed
    if round_pause:
        return
    to_remove_shots = []
    to_remove_targets = []
    for shot in tower_shots:
        shot[0] += 3 * math.cos(shot[3])
        shot[1] += 3 * math.sin(shot[3])
        if (shot[0] > region + 100 or shot[0] < -region or
                shot[1] > region + 100 or shot[1] < -region):
            to_remove_shots.append(shot)
            continue
        for t in targets:
            if t in to_remove_targets:
                continue
            dx = shot[0] - t[0]
            dy = shot[1] - t[1]
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < 40:
                player_score += 1
                enemies_killed += 1
                to_remove_shots.append(shot)
                to_remove_targets.append(t)
                break
    for shot in to_remove_shots:
        if shot in tower_shots:
            tower_shots.remove(shot)
    for t in to_remove_targets:
        if t in targets:
            targets.remove(t)
            if enemies_killed >= kills_to_advance:
                next_round()
            else:
                max_enemies = (
                    enemy_count_per_round[current_round-1]
                    if current_round <= len(enemy_count_per_round)
                    else enemy_count_per_round[-1] + 2 * (current_round - len(enemy_count_per_round))
                )
                if len(targets) < max_enemies:
                    spawn_enemies(1)

def enemy_pulse():
    global target_pulse_t, target_pulse
    target_pulse_t += 0.01
    target_pulse = 1.0 + 0.4 * math.cos(target_pulse_t)

def enemy_angle():
    angles = []
    for t in targets:
        dx, dy = player_position[0] - t[0], player_position[1] - t[1]
        ang = math.degrees(math.atan2(dy, dx)) - 90
        angles.append((ang + 360) % 360)
    return angles

def crosshair():
    if v_enable:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 800, 0, 650)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glColor3f(0, 0, 0)
        glBegin(GL_LINES)
        glVertex2f(400 - 10, 325)
        glVertex2f(400 + 10, 325)
        glVertex2f(400, 325 - 10)
        glVertex2f(400, 325 + 10)
        glEnd()
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

def spawn_enemies(count=target_number):
    global targets
    max_enemies = enemy_count_per_round[current_round - 1] if current_round <= len(enemy_count_per_round) else 15
    if len(targets) + count > max_enemies:
        count = max(0, max_enemies - len(targets))
    for _ in range(count):
        x = random.uniform(-region + 50, region - 50)
        y = random.uniform(-region + 50, region - 50)
        z = random.uniform(0, 10)
        while abs(x) < 200:
            x = random.uniform(-region + 100, region - 100)
        while abs(y) < 200:
            y = random.uniform(-region + 100, region - 100)
        targets.append([x, y, z])

def update_enemy_shots():
    global enemy_shots, player_health, game_end
    if round_pause:
        return
    to_remove = []
    for shot in enemy_shots:
        shot[0] += 1.5 * math.cos(shot[3])
        shot[1] += 1.5 * math.sin(shot[3])
        if (shot[0] > GRID_LENGTH + 100 or shot[0] < -GRID_LENGTH or shot[1] > GRID_LENGTH + 100 or shot[1] < -GRID_LENGTH):
            to_remove.append(shot)
            continue
        dx = player_position[0] - shot[0]
        dy = player_position[1] - shot[1]
        dist = math.sqrt(dx*dx + dy*dy)
        if dist < castle_radius:
            if not cheat:
                player_health -= enemy_shot_damage
                if player_health <= 0:
                    game_end = True
                    targets.clear()
                    shots.clear()
                    enemy_shots.clear()
            to_remove.append(shot)
    for shot in to_remove:
        if shot in enemy_shots:
            enemy_shots.remove(shot)

def next_round():
    global current_round, castle_radius, target_number, enemies_killed, region, round_pause, target_speed
    global player_health, player_max_health, kills_to_advance
    current_round += 1
    enemies_killed = 0
    target_speed += 0.25
    round_pause = True
    kills_to_advance += 10
    player_health = player_max_health
    if current_round < 5:
        castle_radius += 20
        region += 300
    if current_round <= len(enemy_count_per_round):
        target_number = enemy_count_per_round[current_round-1]
    else:
        target_number = enemy_count_per_round[-1] + 2 * (current_round - len(enemy_count_per_round))
    spawn_enemies(target_number)

def reset_game():
    global game_end, first_person_view, cheat, v_enable, misses, region, towers, target_speed, current_round
    global player_health, player_max_health, player_score, player_position, gun_rotation, castle_radius
    global tower_shots, tower_shot_timers, round_pause, round_choice_made
    game_end, first_person_view = False, False
    cheat, v_enable, round_pause, round_choice_made = False, False, False, False
    player_position = [0, 0, 0]
    towers = []
    region = 600
    target_speed = 0.025
    current_round = 1
    castle_radius = 60
    gun_rotation, player_health, player_max_health, player_score, misses = 180, 100, 100, 0, 0
    shots.clear()
    targets.clear()
    tower_shots.clear()
    tower_shot_timers.clear()
    spawn_enemies()

def keyboardListener(key, x, y):
    global cheat, first_person_view, game_end, v_enable, gun_rotation,camera_position, camera_angle
    global player_position, player_speed, player_rotation, player_health, player_max_health, player_score, misses
    global round_pause, round_choice_made, towers, tower_shot_timers, tower_placement_mode, placement_marker_position

    if round_pause:
        if tower_placement_mode:
            if key == b's' and placement_marker_position[1] < region - 50:
                placement_marker_position[1] += 50
            elif key == b'w' and placement_marker_position[1] > -region + 50:
                placement_marker_position[1] -= 50
            elif key == b'd' and placement_marker_position[0] > -region + 50:
                placement_marker_position[0] -= 50
            elif key == b'a' and placement_marker_position[0] < region - 50:
                placement_marker_position[0] += 50
            elif key == b'\r':
                if (abs(placement_marker_position[0]) > castle_region or
                        abs(placement_marker_position[1]) > castle_region):
                    if len(towers) < 5:
                        towers.append(tuple(placement_marker_position))
                        tower_shot_timers[len(towers)-1] = random.randint(60, tower_shot_cooldown)
                    tower_placement_mode = False
                    round_pause = False
                    round_choice_made = True
                    first_person_view = not first_person_view
                    v_enable = first_person_view
                    player_rotation = 2.5 if first_person_view else 5
                else:
                    print("Cannot place a tower inside the castle region!")
            return

        if key == b'1':
            if current_round < 5:
                player_max_health += 100
            player_health = player_max_health
            round_pause = False
            round_choice_made = True
            return
        elif key == b'2':
            if current_round > 4:
                round_choice_made = True
            tower_placement_mode = True
            placement_marker_position = [400, 400]  # Reset marker to the center
            first_person_view = not first_person_view
            v_enable = first_person_view
            player_rotation = 2.5 if first_person_view else 5
            camera_position, camera_angle = (0, 600, 600), 0
            return
        return

    if game_end and key != b'r':
        return
    elif key == b'c' and cheat == True:
        shots.clear()
        cheat = False
    elif key == b'v':
        if first_person_view and cheat:
            v_enable = not v_enable
    elif key == b'r' and game_end:
        reset_game()
    if key == b'p':
        player_health = 1000
    gun_rotation %= 360
    if key == b'd':
        gun_rotation -= 5
    if key == b'a':
        gun_rotation += 5

def specialKeyListener(key, x, y):
    global camera_angle, camera_distance, camera_height, camera_min_height, camera_max_height
    if not game_end:
        if key == GLUT_KEY_UP:
            if camera_height > camera_min_height:
                camera_height -= 20
        elif key == GLUT_KEY_DOWN:
            if camera_height < camera_max_height:
                camera_height += 20
        elif key == GLUT_KEY_LEFT:
            camera_angle -= 5
        elif key == GLUT_KEY_RIGHT:
            camera_angle += 5

def mouseListener(button, state, x, y):
    global first_person_view, player_rotation, v_enable, game_end
    if game_end:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and cheat == False:
        shoot()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_view = not first_person_view
        v_enable = first_person_view
        player_rotation = 2.5 if first_person_view else 5

def setupCamera():
    global camera_position, camera_angle, camera_distance, camera_height
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(100, 1.25, 0.3, 2700)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if first_person_view:
        angle = math.radians(gun_rotation)
        eye_x = player_position[0] + (gun_position[0]*1.2 *math.sin(angle)) - (gun_position[1]*0.6*math.cos(angle))
        eye_y = player_position[1] - (gun_position[0]*1.2 *math.cos(angle)) - (gun_position[1]*0.6*math.sin(angle))
        eye_z = player_position[2] + gun_position[2] + 200
        cen_x = eye_x - math.sin(-angle) * 100
        cen_y = eye_y - math.cos(-angle) * 100
        cen_z = eye_z
        gluLookAt(eye_x, eye_y, eye_z + 50, cen_x, cen_y, cen_z - 30, 0, 0, 1)
    else:
        angle = math.radians(camera_angle)
        x = camera_distance * math.sin(angle)
        y = camera_distance * math.cos(angle)
        z = camera_height
        gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)
def idle():
    global player_score
    enemy_pulse()
    if round_pause:
        glutPostRedisplay()
        return
    if not game_end:
        update_enemies()
        update_enemy_shots()
        update_towers()
        update_tower_shots()
        gun_shot_check()
        detect_target_hits()
    glutPostRedisplay()

def draw_gradient_background():
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 650)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glBegin(GL_QUADS)
    glColor3f(0.63, 0.81, 0.98)
    glVertex2f(0, 650)
    glVertex2f(800, 650)
    glColor3f(0.07, 0.11, 0.21)
    glVertex2f(800, 0)
    glVertex2f(0, 0)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def showScreen():
    global game_end, player_health, player_max_health, player_score, misses, round_pause, tower_placement_mode
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 800, 650)
    draw_gradient_background()
    setupCamera()
    draw_shapes()
    if v_enable:
        crosshair()
    if round_pause:
        if tower_placement_mode:
            glPushMatrix()
            glTranslatef(placement_marker_position[0], placement_marker_position[1], 10)
            glScalef(target_pulse, target_pulse, target_pulse)
            glColor3f(0, 1, 1)
            glutSolidSphere(20, 16, 16)
            glPopMatrix()
            draw_text(200, 400, "Use W, A, S, D to move the marker", color=(1, 1, 0))
            draw_text(200, 350, "Press Enter to place the tower", color=(0, 1, 0))
        else:
            if current_round < 5:
                draw_text(200, 400, f"Round {current_round-1} Completed! More region conquered", color=(1, 1, 0))
                draw_text(200, 350, "Choose your reward:", color=(1, 0.7, 0.2))
                draw_text(200, 300, "Press [1] to increase health by 100", color=(0, 1, 0))
                draw_text(200, 250, "Press [2] to add an extra tower", color=(0, 0.7, 1))
            else:
                draw_text(250, 400, f"Round {current_round-1} Completed!", color=(1, 1, 0))
                draw_text(200, 300, "Press [1] or [2] to continue", color=(0, 1, 0))
    elif not game_end:
        draw_text(10, 650 - 25, f"Castle Health: {player_health}/{player_max_health}", color=(0, 0, 0))
        draw_text(10, 650 - 55, f"Score: {player_score}")
        draw_text(10, 650 - 85, f"Misses: {misses}")
        draw_text(350, 625, f"Round {current_round}", color=(0, 0, 0))
        remaining = kills_to_advance - enemies_killed
        color = (1, 0, 0) if remaining > 5 else (1, 0.5, 0) if remaining > 2 else (0, 1, 0)
        draw_text(580, 650 - 25, f"Enemies to Kill: {remaining}", color=(0, 0, 0))
        draw_text(580, 650 - 55, f"Total Enemies: {len(targets)}")
    else:
        draw_text(10, 650 - 25, f"Game Over! Your Score is {player_score}")
        draw_text(10, 650 - 55, 'Press "R" to RESTART the Game')
    glutSwapBuffers()

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 650)
glutCreateWindow(b"Tower Defense")
spawn_enemies()
glutDisplayFunc(showScreen)
glutIdleFunc(idle)
glutKeyboardFunc(keyboardListener)
glutSpecialFunc(specialKeyListener)
glutMouseFunc(mouseListener)
glutMainLoop()