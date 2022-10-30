import itertools
import math

from objects import *
from settings import *

##### PYGAME INIT #####
pygame.init()
screen = pygame.display.set_mode(WIN_DIMENTIONS, pygame.RESIZABLE)
pygame.display.set_caption("Physics Simulator")
clock = pygame.time.Clock(  )
exit = False

##### INTERNAL VARIABLES #####
render_sprites_list = pygame.sprite.Group()
trail_sprites_list = pygame.sprite.Group()
creating = False
click_pos = (0, 0)
radius = DEFAULT_RADIUS
mass = DEFAULT_MASS
static = False
trail = True
curr_pos = (0, 0)
cmd = ""
stop_time = False
orbit = False

camerax = 0
cameray = 0

cameravx = 0
cameravy = 0

cameraax = 0
cameraay = 0


##### LOGIC #####
def blit_sprites():
    for sprite in render_sprites_list:
        sprite.draw(screen, camerax, cameray)


def create_sprite(pos, m, r, vx, vy, trail, static):
    obj = Obj((pos[0] - camerax, pos[1] - cameray), m, r, vx, vy, trail, static)
    render_sprites_list.add(obj)
    if trail == True:
        trail_sprites_list.add(obj)


def calculate_forces():
    for sprite in render_sprites_list:
        sprite.ax = 0
        sprite.ay = 0
    for pair in list(itertools.combinations(render_sprites_list, 2)):
        d = math.dist([pair[0].x, pair[0].y], [pair[1].x, pair[1].y])
        if pair[0].r + pair[1].r < d:
            try:
                theta = math.atan((pair[1].y - pair[0].y) / (pair[1].x - pair[0].x))
            except:
                theta = math.pi / 2
            F = G * pair[0].m * pair[1].m / (d ** 2)
            Fx = F * math.cos(theta)
            Fy = F * math.sin(theta)
            if pair[0].x < pair[1].x:
                pair[0].ax += Fx / pair[0].m
                pair[0].ay += Fy / pair[0].m
                pair[1].ax += -Fx / pair[1].m
                pair[1].ay += -Fy / pair[1].m
            else:
                pair[0].ax += -Fx / pair[0].m
                pair[0].ay += -Fy / pair[0].m
                pair[1].ax += Fx / pair[1].m
                pair[1].ay += Fy / pair[1].m
        else:
            handle_collision(pair[0], pair[1])


def calculate_pos(dt):
    global camerax, cameray, cameravx, cameravy, cameraax, cameraay
    if dt == 0:
        return

    dt *= TIME_SCALE
    for sprite in render_sprites_list:
        if not sprite.static:
            sprite.update_xy(sprite.x + sprite.vx * dt + 0.5 * sprite.ax * (dt ** 2),
                             sprite.y + sprite.vy * dt + 0.5 * sprite.ay * (dt ** 2))
            sprite.vx += sprite.ax * dt
            sprite.vy += sprite.ay * dt

    camerax += cameravx * dt + 0.5 * cameraax * (dt ** 2)
    cameray += cameravy * dt + 0.5 * cameraay * (dt ** 2)
    cameravx += cameraax * dt
    cameravy += cameraay * dt

    if cameravx >= CAMERA_DECEL_THRESHOLD:
        cameravx -= CAMERA_DECELERATION * dt
    elif -CAMERA_DECEL_THRESHOLD < cameravx < CAMERA_DECEL_THRESHOLD:
        cameravx = 0
    else:
        cameravx += CAMERA_DECELERATION * dt

    if cameravy >= CAMERA_DECEL_THRESHOLD:
        cameravy -= CAMERA_DECELERATION * dt
    elif -CAMERA_DECEL_THRESHOLD < cameravy < CAMERA_DECEL_THRESHOLD:
        cameravy = 0
    else:
        cameravy += CAMERA_DECELERATION * dt


def handle_collision(obj1, obj2):
    R = ((obj2.r ** 3) + (obj1.r ** 3)) ** (1 / 3)
    m = obj1.m + obj2.m

    vx = (obj1.vx * obj1.m + obj2.vx * obj2.m) / m
    vy = (obj1.vy * obj1.m + obj2.vy * obj2.m) / m

    if obj1.static == True:
        obj2.kill()
    elif obj2.static == True:
        obj1.kill()
    else:
        if obj1.r > obj2.r:
            obj2.kill()
        else:
            obj1.kill()
            obj1 = obj2

        obj1.r = R
        obj1.m = m
        obj1.vx = vx
        obj1.vy = vy
        obj1.update_image()


def remove_redundant_sprites():
    for sprite in render_sprites_list:
        if sprite.x > screen.get_width() + SCREEN_ESCAPE + camerax or sprite.x < -SCREEN_ESCAPE - camerax or \
                sprite.y > screen.get_height() + SCREEN_ESCAPE + cameray or sprite.y < -SCREEN_ESCAPE - cameray:
            sprite.kill()


def reset_variables():
    global creating, static, radius, mass, cmd, moon
    creating = False
    static = False
    radius = DEFAULT_RADIUS
    mass = DEFAULT_MASS
    cmd = ""
    camerax = 0
    cameray = 0
    cameraax = 0
    cameraay = 0


def remove_all_sprites():
    for sprite in render_sprites_list:
        sprite.kill()


def get_pos_sprite(pos):
    for sprite in render_sprites_list:
        d = math.dist([sprite.x + camerax, sprite.y + cameray], [pos[0], pos[1]])
        if d < sprite.r:
            return sprite
    return False


def draw_trail():
    for sprite in trail_sprites_list:
        for i in range(len(sprite.trail_hist) - 1):
            p1 = (sprite.trail_hist[i][0] + camerax, sprite.trail_hist[i][1] + cameray)
            p2 = (sprite.trail_hist[i + 1][0] + camerax, sprite.trail_hist[i + 1][1] + cameray)
            if -SCREEN_ESCAPE - camerax < p1[0] < screen.get_width() + SCREEN_ESCAPE + camerax and \
                -SCREEN_ESCAPE - cameray < p1[1] < screen.get_height() + SCREEN_ESCAPE + cameray:
                pygame.draw.line(screen, sprite.colour, p1, p2, width=2)


##### RUN #####
while not exit:
    dt = clock.tick(FPS)
    if stop_time:
        dt = 0
    screen.fill(BG_COLOR)

    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN and not creating:
            if event.button == pygame.BUTTON_LEFT:
                creating = True
                click_pos = pygame.mouse.get_pos()
                curr_pos = click_pos

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                stop_time = not stop_time
            if event.key == pygame.K_t:
                trail = not trail
            if event.key == pygame.K_w:
                cameravy += CAMERA_VELOCITY
            if event.key == pygame.K_s:
                cameravy -= CAMERA_VELOCITY
            if event.key == pygame.K_a:
                cameravx += CAMERA_VELOCITY
            if event.key == pygame.K_d:
                cameravx -= CAMERA_VELOCITY
            if event.key == pygame.K_r and not creating:
                remove_all_sprites()
                reset_variables()
                iter = random.randint(3, 15)
                for i in range(iter):
                    create_sprite((random.randint(0, screen.get_width()) + camerax,
                                   random.randint(0, screen.get_height()) + cameray),
                                  random.randint(5, 200) * 10, random.randint(1, 25),
                                  random.randint(-100, 100) * VELOCITY_SCALE,
                                  random.randint(-100, 100) * VELOCITY_SCALE, trail, static)
                reset_variables()
            if event.key == pygame.K_q:
                remove_all_sprites()
        if event.type == pygame.MOUSEBUTTONDOWN and creating:
            if event.button == pygame.BUTTON_WHEELUP:
                radius += 5
            if event.button == pygame.BUTTON_WHEELDOWN:
                if radius >= 10:
                    radius -= 5

        if event.type == pygame.MOUSEMOTION and creating:
            curr_pos = pygame.mouse.get_pos()

        if event.type == pygame.KEYDOWN and creating:
            if event.key == pygame.K_c:
                static = True
            else:
                cmd += event.unicode

        if event.type == pygame.MOUSEBUTTONUP and creating:
            if event.button == pygame.BUTTON_LEFT:
                pos = pygame.mouse.get_pos()
                sp = get_pos_sprite(pos)
                if sp != False:
                    d = math.dist([sp.x, sp.y], [click_pos[0], click_pos[1]])
                    try:
                        theta = math.atan((click_pos[1] - sp.y) / (click_pos[0] - sp.x))
                    except:
                        theta = math.pi / 2
                    v = (G * sp.m / d) ** (1 / 2)

                    if sp.x < click_pos[0]:
                        vx = v * math.sin(theta)
                        vy = -v * math.cos(theta)
                    else:
                        vx = -v * math.sin(theta)
                        vy = v * math.cos(theta)
                else:
                    vx = (pos[0] - click_pos[0]) * VELOCITY_SCALE
                    vy = (pos[1] - click_pos[1]) * VELOCITY_SCALE
                try:
                    mass = int(cmd)
                except:
                    pass
                create_sprite(click_pos, mass, radius, vx, vy, trail, static)
                reset_variables()

        if event.type == pygame.QUIT:
            exit = True

    remove_redundant_sprites()

    if len(render_sprites_list) >= 2:
        calculate_forces()
    if len(render_sprites_list) != 0:
        calculate_pos(dt)

    draw_trail()
    blit_sprites()

    if creating:
        pygame.draw.circle(screen, BLUE, click_pos, radius, 1)
        if not static:
            pygame.draw.line(screen, RED, click_pos, curr_pos, width=2)

    pygame.display.update()
