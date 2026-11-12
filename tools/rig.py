import math, os, subprocess
from PIL import Image, ImageDraw

W, H, SS = 960, 540, 2          # output size, supersampling
FPS = 30
BG = (46, 34, 32); MAT = (226, 211, 199); MAT_EDGE = (196, 178, 165); FLOOR = (64, 49, 46)
NEAR = (255, 244, 238); FAR = (222, 196, 188); SKIN_LINE = (46, 34, 32)
L = dict(torso=0.56, neck=0.08, head=0.115, ua=0.30, fa=0.28, th=0.44, sh=0.44, foot=0.11)
SCALE = 330           # px per unit at output size
ORIGIN = (W*0.5, H*0.80)   # floor point under pelvis x=0

def d(a): return (math.cos(math.radians(a)), math.sin(math.radians(a)))
def add(p, a, l): v = d(a); return (p[0]+v[0]*l, p[1]+v[1]*l)

def ik(root, target, l1, l2, bend_up=True):
    dx, dy = target[0]-root[0], target[1]-root[1]
    dist = max(1e-6, min(math.hypot(dx, dy), l1+l2-1e-4))
    a0 = math.degrees(math.atan2(dy, dx))
    c = (l1*l1 + dist*dist - l2*l2) / (2*l1*dist)
    alpha = math.degrees(math.acos(max(-1, min(1, c))))
    cands = []
    for s in (1, -1):
        j = add(root, a0 + s*alpha, l1)
        cands.append(j)
    j = max(cands, key=lambda p: p[1]) if bend_up else min(cands, key=lambda p: p[1])
    a2 = math.degrees(math.atan2(target[1]-j[1], target[0]-j[0]))
    end = add(j, a2, l2)
    return j, end

def solve(p):
    P = (p['px'], p['py'])
    N = add(P, p['torso'], L['torso'])
    headc = add(N, p['torso'] + p.get('head', 0), L['neck'] + L['head'])
    out = dict(P=P, N=N, head=headc, limbs={})
    for side in ('n', 'f'):
        # arms
        if 'hand_'+side in p:
            e, h = ik(N, p['hand_'+side], L['ua'], L['fa'], p.get('elbow_up_'+side, True))
        else:
            off = p['torso'] if p.get('arm_rel') else 0
            e = add(N, p['ua_'+side] + off, L['ua']); h = add(e, p['fa_'+side] + off, L['fa'])
        # legs
        if 'foot_'+side in p:
            k, a = ik(P, p['foot_'+side], L['th'], L['sh'], p.get('knee_up_'+side, True))
            sh_ang = math.degrees(math.atan2(a[1]-k[1], a[0]-k[0]))
        else:
            k = add(P, p['th_'+side], L['th']); sh_ang = p['sh_'+side]; a = add(k, sh_ang, L['sh'])
        if 'foot_abs_'+side in p:
            toe = add(a, p['foot_abs_'+side], L['foot'])
        else:
            toe = add(a, sh_ang + p.get('ft_'+side, 0), L['foot'])
        out['limbs'][side] = dict(e=e, h=h, k=k, a=a, toe=toe)
    return out

MAT_TOP = 12/330   # top of the mat, in body units
def ground(sol, pose):
    """Shift the whole body so its lowest point rests on the mat (no floating, no sinking)."""
    if pose.get('top_view') or not pose.get('ground', True):
        return sol
    pts = [(sol['P'], 0.10), (sol['N'], 0.085), (sol['head'], L['head'])]
    mid = ((sol['P'][0]+sol['N'][0])/2, (sol['P'][1]+sol['N'][1])/2)
    pts.append((mid, 0.085))
    for limb in sol['limbs'].values():
        pts += [(limb['e'], 0.036), (limb['h'], 0.026), (limb['k'], 0.056), (limb['a'], 0.03), (limb['toe'], 0.016)]
    low = min(p[1] - r for p, r in pts)
    dy = pose.get('surface', MAT_TOP) - low
    def sh(p): return (p[0], p[1] + dy)
    out = dict(sol, P=sh(sol['P']), N=sh(sol['N']), head=sh(sol['head']), limbs={})
    for side, limb in sol['limbs'].items():
        out['limbs'][side] = {k: sh(v) for k, v in limb.items()}
    return out

def lerp(a, b, t):
    if isinstance(a, str) or a is None: return a
    if isinstance(a, tuple): return tuple(lerp(x, y, t) for x, y in zip(a, b))
    if isinstance(a, bool): return a if t < 0.5 else b
    return a + (b - a) * t

def blend(p, q, t):
    t = 0.5 - 0.5*math.cos(math.pi*t)    # ease in-out
    r = {}
    for k in p:
        r[k] = lerp(p[k], q.get(k, p[k]), t) if k in q else p[k]
    return r

def pose_at(keys, t, period):
    """keys: list of (time_seconds, pose); loops back to the first."""
    t = t % period
    seq = keys + [(period, keys[0][1])]
    for (t0, p0), (t1, p1) in zip(seq, seq[1:]):
        if t0 <= t <= t1:
            return blend(p0, p1, 0 if t1 == t0 else (t - t0)/(t1 - t0))
    return keys[0][1]

def px(pt):
    return (ORIGIN[0]*SS + pt[0]*SCALE*SS, ORIGIN[1]*SS - pt[1]*SCALE*SS)

def seg(dr, a, b, w, col):
    A, B = px(a), px(b); r = w*SS/2
    dr.line([A, B], fill=col, width=int(w*SS))
    for c in (A, B): dr.ellipse([c[0]-r, c[1]-r, c[0]+r, c[1]+r], fill=col)

def draw(sol, props=()):
    im = Image.new('RGB', (W*SS, H*SS), BG)
    dr = ImageDraw.Draw(im)
    fy = ORIGIN[1]*SS
    dr.rectangle([0, fy, W*SS, H*SS], fill=FLOOR)
    dr.rounded_rectangle([W*SS*0.1, fy-10*SS, W*SS*0.9, fy+8*SS], radius=8*SS, fill=MAT)
    dr.line([W*SS*0.1+8*SS, fy-10*SS, W*SS*0.9-8*SS, fy-10*SS], fill=MAT_EDGE, width=2*SS)
    for pr in props: pr(dr)
    f, n = sol['limbs']['f'], sol['limbs']['n']
    P, N = sol['P'], sol['N']
    # far limbs
    seg(dr, P, f['k'], 30, FAR); seg(dr, f['k'], f['a'], 25, FAR); seg(dr, f['a'], f['toe'], 18, FAR)
    seg(dr, N, f['e'], 21, FAR); seg(dr, f['e'], f['h'], 17, FAR)
    # torso: hips to shoulders, tapered with a waist
    mid = ((P[0]+N[0])/2, (P[1]+N[1])/2)
    seg(dr, P, mid, 46, NEAR); seg(dr, mid, N, 48, NEAR)
    # neck + head
    hc = sol['head']; neck_end = ((N[0]*0.45+hc[0]*0.55), (N[1]*0.45+hc[1]*0.55))
    seg(dr, N, neck_end, 16, NEAR)
    c = px(hc); r = L['head']*SCALE*SS
    dr.ellipse([c[0]-r, c[1]-r, c[0]+r, c[1]+r], fill=NEAR)
    # near limbs (on top)
    seg(dr, P, n['k'], 32, NEAR); seg(dr, n['k'], n['a'], 26, NEAR); seg(dr, n['a'], n['toe'], 18, NEAR)
    seg(dr, N, n['e'], 22, NEAR); seg(dr, n['e'], n['h'], 18, NEAR)
    return im.resize((W, H), Image.LANCZOS)

def render(name, keys, period, out_dir='out', props=()):
    os.makedirs(out_dir, exist_ok=True)
    frames = int(round(period*FPS))
    tmp = os.path.join(out_dir, name + '_frames'); os.makedirs(tmp, exist_ok=True)
    for i in range(frames):
        pose = pose_at(keys, i/FPS, period)
        draw(ground(solve(pose), pose), props).save(f'{tmp}/{i:04d}.png')
    out = os.path.join(out_dir, name + '.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{tmp}/%04d.png',
                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'medium', '-crf', '26',
                    '-movflags', '+faststart', out], check=True)
    subprocess.run(['rm', '-rf', tmp])
    return out
