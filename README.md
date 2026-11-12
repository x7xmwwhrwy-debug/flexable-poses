# flexable-poses

Downloadable Pilates poses for the FlexAble iPhone app. The app reads `catalog.json` and downloads
`videos/<id>.mp4`, so new poses reach users without an app update.

- `catalog.json` – every downloadable pose. `status: draft` is only shown to the reviewer; `live` is shown to everyone.
- `poses/<id>.py` – the animation keyframes and details for each pose.
- `tools/` – the animation rig (`rig.py`, `body.py`, `mat.py`, `equip.py`) and `pose.py` to render and publish.
- `checks/<id>.png` – four frames from each video, for a quick visual check.

Poses come from requests sent in the app; feedback and approvals are stored in FlexAble's CloudKit database.
