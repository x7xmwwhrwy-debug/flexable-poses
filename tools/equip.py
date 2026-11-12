"""Pilates apparatus animations: Reformer, Chair, Barrel, Cadillac.

Same figure and rig as mat.py. Each scene draws its apparatus from the current pose, so the
moving parts (carriage, pedal, bars, springs, straps) always meet the hands and feet.
Units are roughly metres; y is up, the floor is y = 0, head to the left unless stated.
"""
import math, sys
import body, rig
from rig import render, SS, L, add, d

WOOD = (156, 112, 80); WOOD_D = (122, 86, 62); WOOD_L = (182, 138, 102)
UPH = (226, 211, 199); UPH_EDGE = (196, 178, 165)
METAL = (176, 178, 184); METAL_D = (128, 130, 136)
STRAP = (206, 176, 146); SPRING = (214, 120, 104)

def P_(pt): return rig.px(pt)
def poly(dr, pts, col): dr.polygon([P_(p) for p in pts], fill=col)
def box(dr, x0, y0, x1, y1, col, r=0.02):
    a, b = P_((x0, y1)), P_((x1, y0))
    dr.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=max(1, r*rig.SCALE*SS), fill=col)
def line(dr, a, b, w, col):
    A, B = P_(a), P_(b); dr.line([A, B], fill=col, width=max(1, int(w*SS)))
    for c in (A, B):
        r = w*SS/2; dr.ellipse([c[0]-r, c[1]-r, c[0]+r, c[1]+r], fill=col)
def dot(dr, c, r, col):
    C = P_(c); R = r*rig.SCALE*SS; dr.ellipse([C[0]-R, C[1]-R, C[0]+R, C[1]+R], fill=col)
def spring(dr, a, b, coils=9, amp=0.018, col=SPRING, w=3):
    ang = math.degrees(math.atan2(b[1]-a[1], b[0]-a[0])); n = d(ang+90)
    pts = [a]
    for i in range(1, coils*2):
        t = i/(coils*2); s = amp if i % 2 else -amp
        pts.append((a[0]+(b[0]-a[0])*t + n[0]*s, a[1]+(b[1]-a[1])*t + n[1]*s))
    pts.append(b)
    dr.line([P_(p) for p in pts], fill=col, width=int(w*SS), joint='curve')
    dot(dr, a, 0.012, METAL_D); dot(dr, b, 0.012, METAL_D)

def cur(): return rig._current_pose

# ---------------------------------------------------------------- Reformer
# Frame from x=-1.30 (head end, risers) to 1.22 (foot end, foot bar). Carriage top at y=0.42.
# Carriage spans [car-0.78, car+0.22]; shoulder blocks at car-0.45. Home (springs short) = car 0.36.
R_TOP = 0.42; BAR = (0.98, 0.80); PULLEY = (-1.27, 0.66)
def reformer(dr):
    p = cur(); c = p.get('car', 0.36)
    box(dr, -1.36, 0.20, 1.26, 0.30, WOOD)                      # frame rails
    for x in (-1.30, 1.18): box(dr, x-0.05, 0.0, x+0.05, 0.22, WOOD_D)     # legs
    box(dr, -1.33, 0.30, -1.22, 0.70, WOOD_D)                   # risers at the head end
    dot(dr, PULLEY, 0.03, METAL)
    line(dr, (1.15, 0.30), (BAR[0], BAR[1]), 7, METAL)          # foot bar upright
    dot(dr, BAR, 0.032, METAL)
    spring(dr, (c+0.20, 0.33), (1.10, 0.33), coils=max(4, int(6 + (0.36-c)*18)))   # springs stretch as it moves
    box(dr, c-0.80, 0.30, c+0.22, R_TOP, UPH, r=0.03)          # carriage
    box(dr, c-0.80, R_TOP-0.012, c+0.22, R_TOP, UPH_EDGE, r=0.004)
    box(dr, c-0.82, R_TOP-0.02, c-0.62, R_TOP+0.05, UPH, r=0.025)   # headrest
    if p.get('box'):                                             # short box on top of the carriage
        bx = p['box']; box(dr, c+bx[0], R_TOP, c+bx[1], R_TOP+0.26, WOOD_L, r=0.02)
    else:
        box(dr, c-0.47, R_TOP, c-0.40, R_TOP+0.14, WOOD_L, r=0.02)  # shoulder blocks
    for k in ('rope_n', 'rope_f'):                               # straps from the pulleys to hands/feet
        if k in p: line(dr, PULLEY, p[k], 2.5, STRAP)

def rope_to(p, side, part):
    """Strap ends at the solved hand or foot of this pose (filled after solve via hook)."""
    p['rope_'+side] = ('@', part)

# ---------------------------------------------------------------- Chair (Wunda chair), pedal on the left
C_TOP = 0.62
def chair(dr):
    p = cur(); sd = p.get('side', -1); tip = p.get('pedal', (0.58*sd, 0.30))
    hinge = (-0.18*sd, 0.10)
    spring(dr, (-0.20, 0.06), ((hinge[0]+tip[0])*0.5 + 0.02, (hinge[1]+tip[1])*0.5 - 0.01), coils=5)
    box(dr, -0.32, 0.0, 0.32, C_TOP, WOOD, r=0.03)                 # box
    box(dr, -0.33, C_TOP-0.03, 0.33, C_TOP+0.04, UPH, r=0.025)    # seat
    line(dr, hinge, tip, 9, METAL)                                # pedal lever
    line(dr, (tip[0]-0.02, tip[1]), (tip[0]+0.06, tip[1]), 12, METAL_D)

# ---------------------------------------------------------------- Ladder barrel, ladder on the right
B_C = (0.0, 0.48); B_R = 0.40
def barrel(dr):
    box(dr, -0.42, 0.0, 0.42, 0.50, WOOD, r=0.02)                  # base
    poly(dr, [(B_C[0]+B_R*math.cos(math.radians(a)), B_C[1]+B_R*math.sin(math.radians(a))) for a in range(0, 181, 6)],
         UPH)
    box(dr, 0.40, 0.30, 0.78, 0.36, WOOD_D)                        # rails to the ladder
    for x in (0.78, 0.90): box(dr, x-0.03, 0.0, x+0.03, 1.22, WOOD_D)
    for y in (0.25, 0.45, 0.65, 0.85, 1.05): line(dr, (0.75, y), (0.93, y), 6, WOOD_L)

# ---------------------------------------------------------------- Cadillac (trapeze table)
T_TOP = 0.66
def cadillac(dr):
    p = cur()
    for x in (-1.02, 1.02): box(dr, x-0.035, 0.0, x+0.035, 1.98, METAL_D)   # uprights
    box(dr, -1.06, 1.94, 1.06, 2.00, METAL_D)                                # top frame
    for x in (-0.95, 0.95): box(dr, x-0.04, 0.0, x+0.04, T_TOP-0.05, WOOD_D)
    box(dr, -1.0, T_TOP-0.10, 1.0, T_TOP, UPH, r=0.03)                       # table
    box(dr, -1.0, T_TOP-0.012, 1.0, T_TOP, UPH_EDGE, r=0.004)
    if 'bar' in p:                                                           # push-through / roll-down bar
        piv, end, top = p['bar']
        line(dr, piv, end, 8, METAL); dot(dr, piv, 0.03, METAL_D)
        if top: spring(dr, top, end, coils=7)
    for k in ('spr_n', 'spr_f'):                                             # leg/arm springs to a solved point
        if k in p: spring(dr, p[k][0], p[k][1], coils=8, w=2.5)
    if p.get('trapeze'):
        tx, ty = p['trapeze']
        line(dr, (tx-0.25, 1.96), (tx-0.25, ty), 2.5, STRAP); line(dr, (tx+0.25, 1.96), (tx+0.25, ty), 2.5, STRAP)
        line(dr, (tx-0.27, ty), (tx+0.27, ty), 7, METAL)

SCENES = {'reformer': reformer, 'chair': chair, 'barrel': barrel, 'cadillac': cadillac}

# Some apparatus parts attach to a solved hand/foot: resolve ('@', 'h'|'a'|...) after solving.
_orig_solve = rig.solve
def _solve(p):
    sol = _orig_solve(p)
    for k in ('rope_n', 'rope_f'):
        if isinstance(p.get(k), tuple) and p[k] and p[k][0] == '@':
            side, part = k[-1], p[k][1]
            p[k] = sol['limbs'][side][part]
    for k in ('spr_n', 'spr_f'):
        if isinstance(p.get(k), tuple) and isinstance(p[k][1], tuple) and p[k][1][0] == '@':
            p[k] = (p[k][0], sol['limbs'][k[-1]][p[k][1][1]])
    return sol
rig.solve = _solve

# ---------------------------------------------------------------- pose helpers
def lie(car, **kw):      # on the carriage, head on the headrest, shoulders against the blocks
    p = dict(scene='reformer', car=car, px=car+0.12, py=R_TOP+0.10, torso=180, head=0, surface=R_TOP,
             ua_n=-6, fa_n=-6, ua_f=-6, fa_f=-6, th_n=0, sh_n=0, th_f=0, sh_f=0, ft_n=0, ft_f=0)
    p.update(kw); return p

def feet_on_bar(p, heels=False):
    # toes (or heels) wrapped over the foot bar
    if heels:
        a = (BAR[0]-0.02, BAR[1]+0.035); fa = 92
    else:
        a = (BAR[0]-0.05, BAR[1]-0.055); fa = 62
    p.update(foot_n=a, foot_f=(a[0]+0.01, a[1]), foot_abs_n=fa, foot_abs_f=fa, ground=False); return p

def sol_circle(c1, r1, c2, r2, upper=True):
    dx, dy = c2[0]-c1[0], c2[1]-c1[1]; dd = math.hypot(dx, dy)
    dd = min(dd, r1+r2-1e-6)
    a = (r1*r1 - r2*r2 + dd*dd) / (2*dd); h = math.sqrt(max(0, r1*r1 - a*a))
    mx, my = c1[0]+a*dx/dd, c1[1]+a*dy/dd
    cands = [(mx + h*dy/dd, my - h*dx/dd), (mx - h*dy/dd, my + h*dx/dd)]
    return max(cands, key=lambda q: q[1]) if upper else min(cands, key=lambda q: q[1])

def plank(car, hip_drop=0.0, **kw):
    """Long-stretch plank: hands on the foot bar, balls of the feet against the shoulder blocks."""
    ank = (car-0.38, R_TOP+0.10)
    leg = L['th']+L['sh']
    N = sol_circle(BAR, 0.54, ank, leg+L['torso'], upper=True)
    tor = math.degrees(math.atan2(N[1]-ank[1], N[0]-ank[0]))
    P = add(N, tor+180, L['torso']); P = (P[0], P[1]-hip_drop)
    t2 = math.degrees(math.atan2(N[1]-P[1], N[0]-P[0]))
    p = dict(scene='reformer', car=car, px=P[0], py=P[1], torso=t2, head=-4, ground=False,
             hand_n=BAR, hand_f=(BAR[0]+0.01, BAR[1]), elbow_up_n=False, elbow_up_f=False,
             foot_n=ank, foot_f=(ank[0]+0.01, ank[1]), knee_up_n=False, knee_up_f=False,
             foot_abs_n=-55, foot_abs_f=-55, ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=0, sh_f=0)
    p.update(kw); return p

def stand_pike(car, hip, tor, **kw):
    """Feet on the carriage against the shoulder blocks, hands on the foot bar (elephant, snake)."""
    ank = (car-0.36, R_TOP+0.045)
    p = dict(scene='reformer', car=car, px=hip[0], py=hip[1], torso=tor, head=-10, ground=False,
             hand_n=BAR, hand_f=(BAR[0]+0.01, BAR[1]), elbow_up_n=False, elbow_up_f=False,
             foot_n=ank, foot_f=(ank[0]+0.015, ank[1]), knee_up_n=False, knee_up_f=False,
             foot_abs_n=0, foot_abs_f=0, ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=0, sh_f=0)
    p.update(kw); return p

def hip_for(ank, tor_dir_from_hip_to_feet, length=None):
    return add(ank, tor_dir_from_hip_to_feet+180, length or (L['th']+L['sh'])*0.995)

E = {}   # name -> (keys, period, scale, origin_y)

# ======================= REFORMER =======================
SC_R = (300, 0.80)
bent = feet_on_bar(lie(0.36)); ext = feet_on_bar(lie(0.0))
E['footwork_parallel'] = ([(0, bent), (1.5, ext), (1.9, ext)], 3.4, *SC_R)
bent = feet_on_bar(lie(0.36), heels=True); ext = feet_on_bar(lie(0.02), heels=True)
E['footwork_v_position'] = ([(0, bent), (1.5, ext), (1.9, ext)], 3.4, *SC_R)

up = lie(0.30, torso=160, head=-14, th_n=44, sh_n=44, th_f=42, sh_f=42, ua_n=-2, fa_n=-2, ua_f=-4, fa_f=-4,
         rope_n=('@', 'h'), rope_f=('@', 'h'))
dn = dict(up, ua_n=-12, fa_n=-12, ua_f=-14, fa_f=-14)
E['hundred_reformer'] = ([(0, up), (0.5, dn), (1.0, up), (1.5, dn)], 2.0, *SC_R)

def circ(car, a):
    return lie(car, th_n=a, sh_n=a, th_f=a-1, sh_f=a-1, ft_n=10, ft_f=10, rope_n=('@', 'toe'), rope_f=('@', 'toe'),
               ua_n=-6, fa_n=-6, ua_f=-6, fa_f=-6)
E['leg_circles_reformer'] = ([(0, circ(0.34, 90)), (0.75, dict(circ(0.26, 70), py=R_TOP+0.105)),
                              (1.5, circ(0.18, 45)), (2.25, dict(circ(0.26, 70), py=R_TOP+0.105))], 3.0, 265, 0.86)

def eleph(car, hip_y):
    ank = (car-0.36, R_TOP+0.045)
    hip = (ank[0] + math.sqrt(max(0.0, 0.876**2 - (hip_y-ank[1])**2)), hip_y)
    return stand_pike(car, hip, -16, head=-38, th_n=0)
E['elephant'] = ([(0, eleph(0.36, 1.27)), (1.4, eleph(0.14, 1.22)), (1.8, eleph(0.14, 1.22))], 3.4, 270, 0.86)

def kneel(car, lean):
    knee = (car-0.02, R_TOP+0.055); ank = (car-0.44, R_TOP+0.05)
    hip = add(knee, 92 - lean, L['th'])
    return dict(scene='reformer', car=car, px=hip[0], py=hip[1], torso=-8-lean*0.4, head=-30, ground=False,
                hand_n=BAR, hand_f=(BAR[0]+0.01, BAR[1]), elbow_up_n=False, elbow_up_f=False,
                foot_n=ank, foot_f=(ank[0]+0.01, ank[1]), knee_up_n=False, knee_up_f=False,
                foot_abs_n=180, foot_abs_f=180, ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=0, sh_f=0)
E['knee_stretches'] = ([(0, kneel(0.30, 0)), (0.7, kneel(0.08, 22)), (1.4, kneel(0.30, 0))], 1.4, 290, 0.84)

E['long_stretch_series'] = ([(0, plank(0.34)), (1.4, plank(0.06)), (1.9, plank(0.06))], 3.4, 280, 0.84)

sit = dict(scene='reformer', car=0.30, box=(-0.55, 0.12), px=0.02, py=R_TOP+0.36, torso=90, head=0, ground=False,
           ua_n=-140, fa_n=-150, ua_f=-138, fa_f=-148, arm_rel=False, th_n=-12, sh_n=-12, th_f=-12, sh_f=-12,
           foot_n=(BAR[0]-0.09, BAR[1]-0.14), foot_f=(BAR[0]-0.08, BAR[1]-0.14), foot_abs_n=70, foot_abs_f=70)
sit['ua_n'], sit['fa_n'], sit['ua_f'], sit['fa_f'] = 20, 160, 18, 158       # arms folded across the chest
rnd = dict(sit, torso=128, head=-22)
E['short_box_series'] = ([(0, sit), (1.4, rnd), (2.2, rnd)], 3.6, 265, 0.88)

pk = eleph(0.36, 1.27); arch = plank(0.06, head=10)
E['snake_twist'] = ([(0, pk), (1.6, arch), (2.2, arch)], 4.4, 270, 0.86)

down = lie(0.34, th_n=42, sh_n=42, th_f=40, sh_f=40, ua_n=176, fa_n=176, ua_f=175, fa_f=175,
           rope_n=('@', 'h'), rope_f=('@', 'h'))
v = lie(0.34, px=0.34+0.05, torso=118, head=-12, th_n=48, sh_n=48, th_f=46, sh_f=46, ua_n=30, fa_n=30, ua_f=28, fa_f=28,
        rope_n=('@', 'h'), rope_f=('@', 'h'))
E['teaser_reformer'] = ([(0, down), (1.8, v), (2.8, v)], 4.8, *SC_R)

over = lie(0.34, px=0.34-0.05, torso=210, head=-30, th_n=176, sh_n=176, th_f=176, sh_f=176,
           hand_n=(0.34-0.62, R_TOP+0.035), hand_f=(0.34-0.60, R_TOP+0.035))
o1 = dict(over, th_n=96, sh_n=96); o2 = dict(over, th_f=96, sh_f=96)
E['control_balance_reformer'] = ([(0, o1), (0.5, o1), (1.2, o2), (1.7, o2)], 2.4, 255, 0.88)

# ======================= CHAIR =======================
SEAT = C_TOP + 0.04
def chair_sit(ped_y, **kw):      # sitting on the seat facing the pedal (pedal on the right)
    tip = (0.58, ped_y)
    p = dict(scene='chair', side=1, pedal=tip, px=0.0, py=SEAT+0.10, torso=90, head=0, ground=False,
             foot_n=(tip[0]-0.04, tip[1]+0.06), foot_f=(tip[0]-0.03, tip[1]+0.06), foot_abs_n=-35, foot_abs_f=-35,
             hand_n=(-0.10, SEAT+0.02), hand_f=(-0.08, SEAT+0.02), elbow_up_n=False, elbow_up_f=False,
             ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=0, sh_f=0)
    p.update(kw); return p
SC_C = (275, 0.92)
E['chair_footwork'] = ([(0, chair_sit(0.42)), (1.4, chair_sit(0.12)), (1.8, chair_sit(0.12))], 3.4, *SC_C)

a = chair_sit(0.12); [a.pop(k) for k in ('hand_n', 'hand_f')]; a.update(ua_n=0, fa_n=0, ua_f=2, fa_f=2)
b = dict(a, ua_n=175, fa_n=178, head=8)
E['chair_seated_spine_twist'] = ([(0, a), (1.2, b), (1.8, b)], 3.0, *SC_C)

def cswan(tor, ped_y):
    tip = (-0.58, ped_y)
    return dict(scene='chair', side=-1, pedal=tip, px=0.12, py=SEAT+0.09, torso=tor, head=-8 if tor < 180 else 6,
                prone=True, ground=False, hand_n=(tip[0]+0.02, tip[1]+0.03), hand_f=(tip[0]+0.03, tip[1]+0.03),
                elbow_up_n=True, elbow_up_f=True, ua_n=0, fa_n=0, ua_f=0, fa_f=0,
                th_n=2, sh_n=2, th_f=4, sh_f=4, ft_n=0, ft_f=0)
E['chair_swan'] = ([(0, cswan(196, 0.15)), (1.6, cswan(162, 0.42)), (2.4, cswan(162, 0.42))], 4.0, *SC_C)

def climb(hip, ped_y, tor):
    tip = (-0.58, ped_y)
    return dict(scene='chair', side=-1, pedal=tip, px=hip[0], py=hip[1], torso=tor, head=-6, ground=False,
                foot_n=(-0.18, SEAT+0.045), foot_abs_n=-2, foot_f=(tip[0]+0.03, tip[1]+0.05), foot_abs_f=-10,
                knee_up_n=True, knee_up_f=True, ua_n=-60, fa_n=-40, ua_f=-120, fa_f=-90,
                th_n=0, sh_n=0, th_f=0, sh_f=0)
E['chair_mountain_climb'] = ([(0, climb((-0.52, 1.06), 0.14, 80)), (1.6, climb((-0.22, 1.46), 0.62, 88)),
                              (2.4, climb((-0.22, 1.46), 0.62, 88))], 4.0, 205, 0.93)

def pike(ped_y, N, head=-60):
    tip = (-0.62, ped_y); ank = (tip[0]+0.03, tip[1]+0.05)
    P = sol_circle(N, L['torso'], ank, 0.875, upper=True)
    tor = math.degrees(math.atan2(N[1]-P[1], N[0]-P[0]))
    return dict(scene='chair', side=-1, pedal=tip, px=P[0], py=P[1], torso=tor, head=head, ground=False,
                hand_n=(-0.27, SEAT+0.02), hand_f=(-0.25, SEAT+0.02), elbow_up_n=False, elbow_up_f=False,
                foot_n=ank, foot_f=(ank[0]+0.01, ank[1]), foot_abs_n=-10, foot_abs_f=-10,
                knee_up_n=False, knee_up_f=False, ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=0, sh_f=0)
E['chair_pike'] = ([(0, pike(0.14, (-0.30, 1.20), head=-20)), (1.6, pike(0.46, (-0.26, 1.22))),
                    (2.4, pike(0.46, (-0.26, 1.22)))], 4.0, 245, 0.90)
E['chair_tendon_stretch'] = ([(0, pike(0.30, (-0.22, 1.12), head=-70)), (1.2, pike(0.10, (-0.22, 1.12), head=-70)),
                              (1.8, pike(0.10, (-0.22, 1.12), head=-70))], 3.0, 245, 0.90)

# ======================= LADDER BARREL =======================
SC_B = (235, 0.90)
def over_barrel(P, tor, ank, **kw):
    p = dict(scene='barrel', px=P[0], py=P[1], torso=tor, head=0, ground=False,
             foot_n=ank, foot_f=(ank[0]+0.01, ank[1]), knee_up_n=True, knee_up_f=True,
             foot_abs_n=-10, foot_abs_f=-10, ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=0, sh_f=0)
    p.update(kw); return p
lo = over_barrel((0.13, 1.0), 198, (0.77, 0.42), prone=True, head=8, ua_n=250, fa_n=250, ua_f=252, fa_f=252,
                 knee_up_n=False, knee_up_f=False)
hi = dict(lo, torso=160, head=-12, ua_n=168, fa_n=168, ua_f=170, fa_f=170)
E['barrel_swan'] = ([(0, lo), (1.6, hi), (2.4, hi)], 4.0, *SC_B)

up = over_barrel((0.02, 0.98), 112, (0.77, 0.62), ua_n=100, fa_n=110, ua_f=-70, fa_f=-70)
arc = dict(up, torso=210, head=12, ua_n=200, fa_n=205, ua_f=225, fa_f=230)
E['barrel_side_stretch'] = ([(0, up), (1.6, arc), (2.4, arc)], 4.0, *SC_B)

def bcirc(a):
    return dict(scene='barrel', px=0.02, py=0.98, torso=205, head=10, ground=False,
                hand_n=(-0.40, 0.52), hand_f=(-0.38, 0.52), elbow_up_n=True, elbow_up_f=True,
                ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=a, sh_n=a, th_f=a-1, sh_f=a-1, ft_n=0, ft_f=0)
E['barrel_leg_circles'] = ([(0, bcirc(108)), (0.75, bcirc(92)), (1.5, bcirc(70)), (2.25, bcirc(92))], 3.0, *SC_B)

sit = over_barrel((0.0, 0.98), 90, (0.80, 0.68), foot_abs_n=60, foot_abs_f=60,
                  ua_n=20, fa_n=160, ua_f=18, fa_f=158, knee_up_n=False, knee_up_f=False)
rnd = dict(sit, torso=130, head=-24)
E['barrel_short_box'] = ([(0, sit), (1.4, rnd), (2.2, rnd)], 3.6, *SC_B)

down = dict(scene='barrel', px=0.0, py=0.98, torso=205, head=8, ground=False, ua_n=200, fa_n=200, ua_f=198, fa_f=198,
            th_n=22, sh_n=22, th_f=20, sh_f=20, ft_n=10, ft_f=10)
vee = dict(down, torso=118, head=-10, ua_n=42, fa_n=42, ua_f=40, fa_f=40, th_n=48, sh_n=48, th_f=46, sh_f=46)
E['barrel_teaser'] = ([(0, down), (1.8, vee), (2.8, vee)], 4.8, *SC_B)

# ======================= CADILLAC =======================
SC_T = (222, 0.90); TS = T_TOP + 0.10
POST_R = (1.0, 1.62)
def rd(tor, hand):
    return dict(scene='cadillac', bar=(hand, hand, POST_R), px=0.05, py=TS, torso=tor, head=-14 if tor > 100 else 0,
                ground=False, hand_n=hand, hand_f=(hand[0]+0.01, hand[1]), elbow_up_n=True, elbow_up_f=True,
                foot_n=(0.88, T_TOP+0.06), foot_f=(0.89, T_TOP+0.06), foot_abs_n=82, foot_abs_f=82,
                ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=0, sh_f=0)
E['cadillac_roll_down'] = ([(0, rd(90, (0.52, 1.20))), (1.8, rd(152, (0.06, 1.08))), (2.6, rd(152, (0.06, 1.08)))],
                           4.6, *SC_T)

POST_L = (-1.0, 1.66)
def lsp(a):
    return dict(scene='cadillac', spr_n=(POST_L, ('@', 'a')), spr_f=(POST_L, ('@', 'a')),
                px=0.15, py=TS, torso=180, head=0, ground=False, hand_n=(-0.96, T_TOP+0.18), hand_f=(-0.95, T_TOP+0.18),
                elbow_up_n=True, elbow_up_f=True, ua_n=0, fa_n=0, ua_f=0, fa_f=0,
                th_n=a, sh_n=a, th_f=a-1, sh_f=a-1, ft_n=10, ft_f=10)
E['cadillac_leg_springs'] = ([(0, lsp(90)), (1.4, lsp(40)), (1.9, lsp(40))], 3.4, *SC_T)

ARM_L = (-1.0, 1.20)
def asp(a):
    return dict(scene='cadillac', spr_n=(ARM_L, ('@', 'h')), spr_f=(ARM_L, ('@', 'h')),
                px=0.30, py=TS, torso=180, head=0, ground=False, ua_n=a, fa_n=a, ua_f=a+1, fa_f=a+1,
                th_n=90, sh_n=0, th_f=88, sh_f=-2, ft_n=0, ft_f=0)
E['cadillac_arm_springs'] = ([(0, asp(172)), (0.7, asp(90)), (1.4, asp(-4)), (1.9, asp(-4)), (2.6, asp(90))], 3.4, *SC_T)

PIV_PT = (1.0, 1.28)
def pt(tor, a):
    end = add(PIV_PT, a, 0.76)
    return dict(scene='cadillac', bar=(PIV_PT, end, (0.62, 1.96)), px=-0.30, py=TS, torso=tor, head=-28 if tor < 80 else 0,
                ground=False, hand_n=end, hand_f=(end[0]+0.01, end[1]), elbow_up_n=True, elbow_up_f=True,
                ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=0, sh_f=0, ft_n=80, ft_f=80)
E['cadillac_push_through'] = ([(0, pt(92, 190)), (1.6, pt(48, 214)), (2.4, pt(48, 214)), (3.4, pt(92, 190))], 4.4, *SC_T)

PIV_LOW = (1.0, 0.70)
def tw(a, py=TS):
    end = add(PIV_LOW, a, 0.82)
    return dict(scene='cadillac', bar=(PIV_LOW, end, (0.95, 1.96)), px=0.08, py=py, torso=180, head=0, ground=False,
                foot_n=add(end, a+180, 0.03), foot_f=add(end, a+180, 0.02), foot_abs_n=a-80, foot_abs_f=a-80,
                knee_up_n=True, knee_up_f=True, ua_n=-6, fa_n=-6, ua_f=-6, fa_f=-6, th_n=0, sh_n=0, th_f=0, sh_f=0)
E['cadillac_tower'] = ([(0, tw(118)), (1.4, tw(150)), (1.9, tw(150))], 3.4, *SC_T)

def hang(hip_y):
    return dict(scene='cadillac', trapeze=(0.0, 1.80), px=-0.02, py=hip_y, torso=92, head=0, ground=False,
                hand_n=(0.0, 1.80), hand_f=(0.02, 1.80), elbow_up_n=False, elbow_up_f=False,
                ua_n=0, fa_n=0, ua_f=0, fa_f=0, th_n=0, sh_n=0, th_f=-2, sh_f=-2, ft_n=0, ft_f=0)
E['cadillac_hanging_pull_ups'] = ([(0, hang(0.92)), (1.2, hang(1.18)), (1.7, hang(1.18))], 3.0, *SC_T)

if __name__ == '__main__':
    names = sys.argv[1:] or list(E)
    for n in names:
        keys, period, scale, oy = E[n]
        rig.SCALE = body.SCALE = scale
        rig.ORIGIN = (rig.W*0.5, rig.H*oy)
        scene = keys[0][1]['scene']
        render(n, keys, period, props=(SCENES[scene],))
        print('rendered', n)
