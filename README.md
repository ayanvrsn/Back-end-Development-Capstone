# Back-end-Development-Capstone

IBM Back-End Development Capstone implementation based on the official IBM Skills Network starter template. Original starter instructions are preserved in `IBM_STARTER_README.md`.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Set `SONGS_SERVICE_URL` and `PICTURES_SERVICE_URL` to the deployed Flask service base URLs. Defaults point to local ports 5001 and 5000. Create an admin account with `python manage.py createsuperuser`. Run tests with `python manage.py test`.

## Evidence and deployment status

`evidence/` contains actual captured command output from local verification. Local test success does not assert IBM Cloud deployment. Docker and Kubernetes files provide a deployment configuration; cloud rollout must be executed and checked separately. No cloud endpoint or screenshot is fabricated.
