# Example pose definition (not published). Copy to poses/<id>.py and run: python3 tools/pose.py render <id>
from mat import S, KB, SIT, PR
a = KB(); b = dict(a, py=0.30, torso=198, head=-18, ua_n=-8, fa_n=-8, ua_f=-8, fa_f=-8)
KEYS = [(0, a), (1.6, b), (2.4, b)]
PERIOD = 4.0
META = dict(name="Example", practiceTypes=["mat"], difficulty="Beginner", muscleGroups=["Glutes", "Core"],
            cue="Peel up one bone at a time.", breath=[dict(inhale=False, text="Lift", seconds=3), dict(inhale=True, text="Lower", seconds=3)],
            pelvis="neutral", timed=False, oneSided=False)
