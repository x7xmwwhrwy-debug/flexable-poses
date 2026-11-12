import math
from PIL import Image, ImageDraw
import rig
from rig import W, H, SS, L, px, d, add, BG, FLOOR, MAT, MAT_EDGE, SCALE

SKIN = (241, 205, 186); SKIN_FAR = (214, 176, 158)
TOP = (255, 246, 240); TOP_FAR = (224, 206, 198)
LEGGINGS = (196, 112, 100); LEGGINGS_FAR = (158, 86, 77)
HAIR = (92, 58, 48)

def taper(dr, a, b, ra, rb, col, bulge=0.0, bulge_side=1):
    """Tapered limb from a (radius ra) to b (radius rb), with an optional mid bulge (muscle)."""
    ang = math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))
    n = d(ang + 90*bulge_side)
    pts_l, pts_r = [], []
    steps = 10
    for i in range(steps+1):
        t = i/steps
        c = (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
        r = ra + (rb-ra)*t
        bump = bulge * math.sin(math.pi*t)
        pts_l.append((c[0]+n[0]*(r+bump), c[1]+n[1]*(r+bump)))
        pts_r.append((c[0]-n[0]*r, c[1]-n[1]*r))
    poly = [px(p) for p in pts_l + pts_r[::-1]]
    dr.polygon(poly, fill=col)
    for c, r in ((a, ra), (b, rb)):
        C = px(c); R = r*SCALE*SS
        dr.ellipse([C[0]-R, C[1]-R, C[0]+R, C[1]+R], fill=col)

def dot(dr, c, r, col):
    C = px(c); R = r*SCALE*SS
    dr.ellipse([C[0]-R, C[1]-R, C[0]+R, C[1]+R], fill=col)

def leg(dr, P, k, a, toe, skin, cloth, flip=1):
    # flip = 1 lying face up / sitting, -1 face down: decides which side is the back of the leg
    taper(dr, P, k, 0.085, 0.056, cloth, bulge=0.012, bulge_side=flip)       # thigh (front of thigh)
    taper(dr, k, a, 0.054, 0.032, cloth, bulge=0.016, bulge_side=-flip)      # calf (back of leg)
    taper(dr, a, toe, 0.030, 0.016, skin)                                     # foot
    sh_ang = math.degrees(math.atan2(a[1]-k[1], a[0]-k[0]))
    toe_ang = math.degrees(math.atan2(toe[1]-a[1], toe[0]-a[0]))
    # heel sits behind the ankle: opposite the toes, on the back-of-leg side
    back = sh_ang - 90*flip
    heel = add(add(a, toe_ang + 180, 0.012), back, 0.014)
    dot(dr, heel, 0.027, skin)

def arm(dr, N, e, h, skin, cloth):
    taper(dr, N, e, 0.046, 0.034, skin, bulge=0.006)
    taper(dr, e, h, 0.032, 0.024, skin)
    ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
    taper(dr, h, add(h, ang, 0.06), 0.026, 0.018, skin)                      # hand
    # short sleeve over the shoulder
    taper(dr, N, add(N, math.degrees(math.atan2(e[1]-N[1], e[0]-N[0])), 0.09), 0.056, 0.045, cloth)

def draw(sol, pose, props=()):
    im = Image.new('RGB', (W*SS, H*SS), BG)
    dr = ImageDraw.Draw(im)
    fy = rig.ORIGIN[1]*SS
    if pose.get('scene'):
        dr.rectangle([0, fy, W*SS, H*SS], fill=FLOOR)          # apparatus scenes: floor only, kit drawn by props
    elif pose.get('top_view'):
        # Seen from above (side-lying): the mat is a big rectangle behind the body
        dr.rounded_rectangle([W*SS*0.10, H*SS*0.22, W*SS*0.90, H*SS*0.86], radius=14*SS, fill=FLOOR)
        dr.rounded_rectangle([W*SS*0.12, H*SS*0.30, W*SS*0.88, H*SS*0.80], radius=12*SS, fill=(116, 100, 92))
    else:
        dr.rectangle([0, fy, W*SS, H*SS], fill=FLOOR)
        dr.rounded_rectangle([W*SS*0.08, fy-12*SS, W*SS*0.92, fy+8*SS], radius=8*SS, fill=MAT)
        dr.line([W*SS*0.08+8*SS, fy-12*SS, W*SS*0.92-8*SS, fy-12*SS], fill=MAT_EDGE, width=2*SS)
    for pr in props: pr(dr)

    f, n = sol['limbs']['f'], sol['limbs']['n']
    P, N, hc = sol['P'], sol['N'], sol['head']
    tor = pose['torso']; flip = -1 if pose.get('prone') else 1
    front = tor - 90*flip

    # far side
    arm(dr, N, f['e'], f['h'], SKIN_FAR, TOP_FAR)
    leg(dr, P, f['k'], f['a'], f['toe'], SKIN_FAR, LEGGINGS_FAR, flip)

    # torso: hips (leggings) → waist → chest (top) → shoulders
    waist = add(P, tor, L['torso']*0.42)
    chest = add(add(P, tor, L['torso']*0.72), front, 0.018)
    taper(dr, P, waist, 0.105, 0.080, LEGGINGS)
    dot(dr, add(P, front + 180, 0.02), 0.075, LEGGINGS)                      # seat
    taper(dr, waist, chest, 0.080, 0.100, TOP)
    taper(dr, chest, N, 0.100, 0.075, TOP)
    # neck and head
    head_dir = tor + pose.get('head', 0)
    neck_top = add(N, head_dir, 0.09)
    taper(dr, N, neck_top, 0.040, 0.034, SKIN)
    dot(dr, hc, L['head'], SKIN)
    fside = head_dir - 90*flip; bside = head_dir + 90*flip
    back = add(hc, bside, 0.02)
    dot(dr, add(back, head_dir, 0.015), L['head']*0.92, HAIR)
    dot(dr, add(hc, fside, 0.035), L['head']*0.80, SKIN)                     # face side stays skin
    dot(dr, add(add(hc, head_dir, 0.06), bside, 0.07), 0.05, HAIR)          # bun
    nose = add(add(hc, fside, L['head']*0.95), head_dir, -0.005)
    dot(dr, nose, 0.018, SKIN)

    # near side on top
    leg(dr, P, n['k'], n['a'], n['toe'], SKIN, LEGGINGS, flip)
    arm(dr, N, n['e'], n['h'], SKIN, TOP)
    return im.resize((W, H), Image.LANCZOS)

# Plug into the renderer
def _draw(sol, props=(), _pose=None):
    return draw(sol, rig._current_pose, props)
_orig_pose_at = rig.pose_at
def _pose_at(keys, t, period):
    p = _orig_pose_at(keys, t, period); rig._current_pose = p; return p
rig.pose_at = _pose_at
rig.draw = _draw
