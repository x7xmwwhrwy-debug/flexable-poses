"""Make or update one downloadable FlexAble Pilates pose.

    python3 tools/pose.py render <id>            # renders videos/<id>.mp4 + checks/<id>.png from poses/<id>.py
    python3 tools/pose.py publish <id>           # renders, then adds/updates catalog.json as a DRAFT (revision +1)
    python3 tools/pose.py status <id> live|draft # change status (live = visible to every user)
    python3 tools/pose.py remove <id>            # take a pose out of the catalog (video kept in git history)
    python3 tools/pose.py list

poses/<id>.py defines:
    KEYS   = [(t_seconds, pose_dict), ...]  built with the helpers from mat.py (S, KB, SIT, PR, BEHIND_HEAD)
             or equip.py (lie, plank, chair_sit, over_barrel, ... with a 'scene' key for apparatus)
    PERIOD = loop length in seconds (one rep)
    SCALE, ORIGIN_Y = optional framing (defaults 330 and 0.80; smaller SCALE shows more)
    META   = dict(name=..., practiceTypes=[...], difficulty="Beginner|Moderate|Advanced", muscleGroups=[...],
                  cue="one short coaching cue", breath=[dict(inhale=True, text="...", seconds=3), ...],
                  pelvis="neutral"|"imprinted"|None, timed=False, oneSided=False, note=None)
The rep length the app uses is the sum of breath seconds, and the video is sped up/slowed to match.
"""
import sys, os, json, datetime, importlib.util, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.argv_saved = sys.argv; sys.argv = [sys.argv[0], '__none__']
import rig, body, mat, equip   # noqa: E402  (mat/equip set up the figure and apparatus)
sys.argv = sys.argv_saved
from PIL import Image

CAT = os.path.join(ROOT, 'catalog.json')

def load_def(pid):
    path = os.path.join(ROOT, 'poses', pid + '.py')
    spec = importlib.util.spec_from_file_location('pose_' + pid, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def render(pid):
    m = load_def(pid)
    rig.SCALE = body.SCALE = getattr(m, 'SCALE', 330)
    rig.ORIGIN = (rig.W * 0.5, rig.H * getattr(m, 'ORIGIN_Y', 0.80))
    scene = m.KEYS[0][1].get('scene')
    props = (equip.SCENES[scene],) if scene else ()
    out = rig.render(pid, m.KEYS, m.PERIOD, out_dir=os.path.join(ROOT, 'videos'), props=props)
    # contact sheet: 4 frames across one loop, to check feet, floating and the move
    frames = []
    for f in (0, 0.25, 0.5, 0.75):
        p = rig.pose_at(m.KEYS, m.PERIOD * f, m.PERIOD)
        frames.append(rig.draw(rig.ground(rig.solve(p), p), props).resize((480, 270)))
    sheet = Image.new('RGB', (960, 540))
    for i, im in enumerate(frames): sheet.paste(im, ((i % 2) * 480, (i // 2) * 270))
    sheet.save(os.path.join(ROOT, 'checks', pid + '.png'))
    return m, out

def load_cat():
    with open(CAT) as f: return json.load(f)

def save_cat(c):
    c['poses'].sort(key=lambda p: p['id'])
    with open(CAT, 'w') as f: json.dump(c, f, indent=2, ensure_ascii=False); f.write('\n')

def publish(pid):
    m, _ = render(pid)
    c = load_cat(); old = next((p for p in c['poses'] if p['id'] == pid), None)
    meta = dict(m.META)
    entry = dict(id=pid, name=meta['name'], practiceTypes=meta['practiceTypes'], difficulty=meta['difficulty'],
                 muscleGroups=meta['muscleGroups'], cue=meta['cue'], breath=meta['breath'],
                 pelvis=meta.get('pelvis'), timed=meta.get('timed', False), oneSided=meta.get('oneSided', False),
                 clipSeconds=float(m.PERIOD), video=f'videos/{pid}.mp4',
                 revision=(old['revision'] + 1) if old else 1,
                 added=old['added'] if old else datetime.date.today().isoformat(),
                 status='draft', note=meta.get('note'))
    c['poses'] = [p for p in c['poses'] if p['id'] != pid] + [entry]
    save_cat(c)
    print(f'{pid}: revision {entry["revision"]} saved as draft')

def status(pid, st):
    assert st in ('live', 'draft')
    c = load_cat()
    for p in c['poses']:
        if p['id'] == pid: p['status'] = st
    save_cat(c); print(pid, '->', st)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'render': render(sys.argv[2]); print('rendered', sys.argv[2])
    elif cmd == 'publish': publish(sys.argv[2])
    elif cmd == 'status': status(sys.argv[2], sys.argv[3])
    elif cmd == 'remove':
        c = load_cat(); c['poses'] = [p for p in c['poses'] if p['id'] != sys.argv[2]]; save_cat(c)
    elif cmd == 'list':
        for p in load_cat()['poses']: print(p['id'], p['status'], 'rev', p['revision'], p['name'])
