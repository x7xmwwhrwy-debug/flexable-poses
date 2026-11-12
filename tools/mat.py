import sys, body, rig
from rig import render

def S(**kw):   # lying on the back, head to the left
    p = dict(px=0, py=0.12, torso=180, head=0, ua_n=-6, fa_n=-6, ua_f=-6, fa_f=-6,
             th_n=0, sh_n=0, th_f=0, sh_f=0, ft_n=0, ft_f=0)
    p.update(kw); return p

def KB(**kw):  # on the back, knees bent, feet flat
    p = S(th_n=55, sh_n=-64, th_f=53, sh_f=-62, foot_abs_n=-7, foot_abs_f=-7,
          foot_n=(0.445, 0.05), foot_f=(0.47, 0.05))   # feet planted flat on the mat (IK)
    p.update(kw); return p

def SIT(**kw): # sitting tall, legs forward, feet flexed
    p = dict(px=0, py=0.10, torso=90, head=0, ua_n=0, fa_n=0, ua_f=2, fa_f=2,
             th_n=0, sh_n=0, th_f=0, sh_f=0, ft_n=80, ft_f=80)
    p.update(kw); return p

def PR(**kw):  # lying face down, head to the left
    p = dict(px=0, py=0.10, torso=180, prone=True, head=0, ua_n=183, fa_n=183, ua_f=184, fa_f=184,
             th_n=0, sh_n=0, th_f=0, sh_f=0, ft_n=0, ft_f=0)
    p.update(kw); return p

BEHIND_HEAD = dict(arm_rel=True, ua_n=-45, fa_n=95, ua_f=-48, fa_f=92)

P = {}

# --- Prep ---
a = KB(hand_n=(-0.38, 0.24), hand_f=(-0.35, 0.235)); b = dict(a, hand_n=(-0.38, 0.27), hand_f=(-0.35, 0.265))
P['breathing_prep'] = ([(0, a), (3, b)], 6.0)

a = KB(); b = dict(a, py=0.30, torso=198, head=-18, ua_n=-8, fa_n=-8, ua_f=-8, fa_f=-8)
P['pelvic_curl_prep'] = ([(0, a), (1.6, b), (2.4, b)], 4.0)

a = KB(sh_n=-78); a.pop('foot_n')           # near leg on FK so it can fold up
b = dict(a, th_n=90, sh_n=0, foot_abs_n=0)
P['knee_folds_prep'] = ([(0, a), (1.2, b), (2.0, b)], 3.2)

a = SIT(ua_n=0, fa_n=0, ua_f=2, fa_f=2)                          # sit tall, both arms reaching forward
b = dict(a, ua_n=175, fa_n=178, head=8)                          # twist: near arm sweeps back, far arm stays forward
P['spine_twist_prep'] = ([(0, a), (1.2, b), (1.8, b)], 3.0)

# --- Beginner ---
up = S(torso=158, head=-12, th_n=42, sh_n=42, th_f=40, sh_f=40, ua_n=2, fa_n=2, ua_f=0, fa_f=0)
dn = dict(up, ua_n=-9, fa_n=-9, ua_f=-11, fa_f=-11)
P['hundred'] = ([(0, up), (0.5, dn), (1.0, up), (1.5, dn)], 2.0)   # one pump per second, 5 in / 5 out

a = S(torso=155, head=-10, th_n=102, sh_n=8, th_f=24, sh_f=24,
      hand_n=(-0.03, 0.53), hand_f=(0.01, 0.50))
b = dict(a, th_n=24, sh_n=24, th_f=102, sh_f=8)
P['single_leg_stretch'] = ([(0, a), (0.35, a), (1.0, b), (1.35, b)], 2.0)

hug = S(torso=155, head=-10, th_n=105, sh_n=0, th_f=103, sh_f=2, ua_n=35, fa_n=5, ua_f=33, fa_f=3)
reach = dict(hug, th_n=36, sh_n=36, th_f=34, sh_f=34, ua_n=168, fa_n=168, ua_f=166, fa_f=166)
P['double_leg_stretch'] = ([(0, hug), (0.4, hug), (1.4, reach), (1.8, reach)], 3.0)

a = SIT(); b = dict(a, torso=52, head=-32, ua_n=-14, fa_n=-14, ua_f=-12, fa_f=-12)
P['spine_stretch'] = ([(0, a), (1.6, b), (2.4, b)], 4.0)

flat = KB(ua_n=-6, fa_n=-6, ua_f=-6, fa_f=-6, th_n=50, sh_n=-70, th_f=48, sh_f=-68)
br = dict(flat, py=0.50, torso=217, head=-37, th_n=8, sh_n=-88, th_f=6, sh_f=-86, ua_n=-12, fa_n=-12, ua_f=-12, fa_f=-12)
P['shoulder_bridge'] = ([(0, flat), (1.6, br), (2.6, br)], 4.2)

side = dict(px=0.05, py=0.41, torso=180, head=-6, top_view=True, arm_rel=True,
            ua_n=-45, fa_n=95, ua_f=-4, fa_f=-2, th_f=-6, sh_f=-6, ft_f=0, th_n=0, sh_n=0, ft_n=0)
fwd = dict(side, th_n=42, sh_n=42, ft_n=60); fwd2 = dict(side, th_n=48, sh_n=48, ft_n=60)
back = dict(side, th_n=-28, sh_n=-28, ft_n=0)
P['side_kick_series'] = ([(0, side), (0.5, fwd), (0.75, fwd2), (1.0, fwd), (1.8, back), (2.2, back)], 3.0)

a = PR(head=-6, ua_n=170, fa_n=170, th_f=8, sh_f=8)
b = PR(head=-6, ua_f=171, fa_f=171, th_n=8, sh_n=8)
P['swimming_prep'] = ([(0, a), (0.6, a), (1.2, b), (1.8, b)], 2.4)

# --- Moderate ---
lie = S(ua_n=178, fa_n=178, ua_f=177, fa_f=177)
up = SIT(torso=55, head=-25, ua_n=-10, fa_n=-10, ua_f=-8, fa_f=-8, ft_n=0, ft_f=0)
P['rollup'] = ([(0, lie), (1.8, up), (2.4, up)], 4.6)

flat = S(); vert = S(th_n=90, sh_n=90, th_f=89, sh_f=89)
over = S(py=0.42, torso=210, head=-30, th_n=176, sh_n=176, th_f=175, sh_f=175, ua_n=-10, fa_n=-10, ua_f=-10, fa_f=-10)
P['roll_over'] = ([(0, flat), (1.0, vert), (2.2, over), (2.8, over), (4.0, vert)], 5.0)

base = S(th_n=90, sh_n=90)
P['single_leg_circle'] = ([(0, dict(base, th_n=108, sh_n=108)), (0.75, dict(base, th_n=92, sh_n=92, py=0.125)),
                           (1.5, dict(base, th_n=74, sh_n=74)), (2.25, dict(base, th_n=90, sh_n=90, py=0.125))], 3.0)

a = S(torso=145, head=-12, th_n=102, sh_n=6, th_f=26, sh_f=26, arm_rel=True,
      ua_n=-80, fa_n=100, ua_f=-30, fa_f=95)              # near elbow reaches towards the knee
b = dict(a, th_n=26, sh_n=26, th_f=102, sh_f=6, ua_n=-30, fa_n=95, ua_f=-80, fa_f=100)
P['criss_cross'] = ([(0, a), (0.4, a), (1.1, b), (1.5, b)], 2.2)

a = S(torso=152, head=-12, th_n=112, sh_n=112, th_f=24, sh_f=24, hand_n=(-0.08, 0.62), hand_f=(-0.05, 0.6))
b = dict(a, th_n=24, sh_n=24, th_f=112, sh_f=112)
P['scissors'] = ([(0, a), (0.3, a), (0.9, b), (1.2, b)], 1.8)

a = SIT(ua_n=0, fa_n=0, ua_f=0, fa_f=0)
b = dict(a, torso=62, head=-22, ua_n=-28, fa_n=-28, ua_f=150, fa_f=150)
P['saw'] = ([(0, a), (1.4, b), (2.0, b)], 3.4)

down = PR(hand_n=(-0.47, 0.04), hand_f=(-0.44, 0.04))
upp = dict(down, torso=152, head=-14)
P['swan_dive'] = ([(0, down), (1.4, upp), (2.0, upp)], 3.4)

# Hips start low (resting on the mat), then lift into one long line on a straight arm
low = dict(px=0, py=0.20, torso=168, head=-4, th_n=-12, sh_n=-12, th_f=-12, sh_f=-12, ft_n=0, ft_f=0,
           ua_n=88, fa_n=88, ua_f=-84, fa_f=-84)
lift = dict(low, py=0.40, torso=160, th_n=-25, sh_n=-25, th_f=-25, sh_f=-25, ua_n=92, fa_n=92, ua_f=-90, fa_f=-90)
P['side_plank'] = ([(0, low), (1.4, lift), (2.6, lift)], 4.0)

a = PR(torso=176, head=-8, ua_n=168, fa_n=168, ua_f=176, fa_f=176, th_n=9, sh_n=9, th_f=3, sh_f=3)
b = dict(a, ua_n=176, fa_n=176, ua_f=168, fa_f=168, th_n=3, sh_n=3, th_f=9, sh_f=9)
P['swimming'] = ([(0, a), (0.3, b)], 0.6)

# --- Advanced ---
lie = S(th_n=42, sh_n=42, th_f=40, sh_f=40, ua_n=176, fa_n=176, ua_f=175, fa_f=175)
v = S(torso=118, head=-12, th_n=48, sh_n=48, th_f=46, sh_f=46, ua_n=40, fa_n=40, ua_f=38, fa_f=38)   # V: lean back, legs and arms reach up
P['teaser'] = ([(0, lie), (1.8, v), (2.8, v)], 4.8)

o = dict(over, th_n=176, sh_n=176, th_f=176, sh_f=176, hand_n=(-0.86, 0.06), hand_f=(-0.84, 0.06), arm_rel=False)
o1 = dict(o, th_n=96, sh_n=96); o2 = dict(o, th_f=96, sh_f=96)
P['control_balance'] = ([(0, o1), (0.5, o1), (1.2, o2), (1.7, o2)], 2.4)

jack = S(py=0.62, torso=262, head=-80, th_n=96, sh_n=96, th_f=95, sh_f=95, ua_n=-10, fa_n=-10, ua_f=-10, fa_f=-10)
P['jackknife'] = ([(0, vert), (1.2, over), (2.0, jack), (2.6, jack), (3.6, over)], 4.6)

lie_h = S(**BEHIND_HEAD); up_h = SIT(torso=58, head=-25, ft_n=80, ft_f=80, **BEHIND_HEAD)
P['neck_pull'] = ([(0, lie_h), (1.8, up_h), (2.4, dict(up_h, torso=90, head=0)), (3.0, up_h)], 5.0)

P['boomerang'] = ([(0, v), (1.4, over), (2.0, over)], 3.6)

star = dict(lift, th_n=8, sh_n=8, ua_n=112, fa_n=118)
P['star'] = ([(0, lift), (1.0, star), (1.8, star)], 3.0)

cv = S(th_n=90, sh_n=90, th_f=89, sh_f=89, ua_n=-8, fa_n=-8, ua_f=-8, fa_f=-8)
P['corkscrew'] = ([(0, dict(cv, th_n=108, sh_n=108, th_f=107, sh_f=107)), (0.9, dict(cv, py=0.17)),
                   (1.8, dict(cv, th_n=72, sh_n=72, th_f=71, sh_f=71)), (2.7, cv)], 3.6)

bow = PR(py=0.05, torso=150, head=-10, th_n=30, sh_n=140, th_f=28, sh_f=138, hand_n=(0.044, 0.653), hand_f=(0.05, 0.64))
bow2 = dict(bow, torso=166, th_n=24, sh_n=132, th_f=22, sh_f=130, hand_n=(0.12, 0.66), hand_f=(0.12, 0.65))
P['rocking'] = ([(0, bow), (0.8, bow2)], 1.6)

SMALL = {'jackknife': 245, 'control_balance': 285, 'roll_over': 300, 'boomerang': 300}

if __name__ == '__main__':
    names = sys.argv[1:] or list(P)
    for n in names:
        keys, period = P[n]
        rig.SCALE = body.SCALE = SMALL.get(n, 330)
        render(n, keys, period)
        print('rendered', n)
