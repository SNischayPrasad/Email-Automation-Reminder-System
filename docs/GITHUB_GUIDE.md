# GitHub Upload & Proof-Building Guide

## Repository details
- **Name:** `Email-Automation-Reminder-System`
- **Description:** Python automation tool that sends personalised, scheduled reminder emails from CSV data, with dry-run mode, SMTP/TLS sending, logging and CSV reports.
- **Topics/tags:** `python` `automation` `email-automation` `smtp` `pandas` `scheduler` `reminder-system` `productivity` `logging` `csv` `streamlit` `python-project`

## Upload steps

1. On GitHub: **New repository** → name above → Public → **do not** add a README (you already have one) → Create.
2. In the project folder:
```powershell
git init
git add .
git status
```
3. **Check `git status`**: `.env` and `venv/` must NOT be listed. If they are, fix `.gitignore` before committing.
```powershell
git commit -m "Initial commit: email automation and reminder system"
git branch -M main
git remote add origin https://github.com/SNischayPrasad/Email-Automation-Reminder-System.git
git push -u origin main
```
4. Later changes:
```powershell
git add .
git commit -m "Add scheduler dry-run screenshots"
git push
```

### Uploading screenshots and outputs
- Save PNGs into `images/` using the names in `images/README.md`, then commit.
- Keep one sample report: rename it to `outputs/sample_report.csv`.
- Keep sample logs: copy `logs/app.log` → `logs/sample_app.log` (the `.gitignore` allows `sample_*.log`).
- On GitHub: About ⚙️ → add the description and topics.

### Security rules
- **Never** commit passwords or app passwords. GitHub is public, and bots scan it for secrets within minutes.
- Commit **`.env.example`** (placeholder values) and keep the real **`.env`** local.
- If you commit a secret by mistake: **revoke the app password immediately** in your Google account. Deleting the file afterwards is not enough because it stays in Git history.

---

## 6-Day Proof Plan (one commit set per day shows steady progress)

| Day | Work | Commit messages | Screenshots |
|---|---|---|---|
| 1: Setup | venv, folders, `requirements.txt`, `.gitignore`, `config.py`, `logger.py` | `chore: project structure and virtual env setup`<br>`feat: add config and logging modules` | `01_folder_structure.png` |
| 2: Data & templates | `sample_data.py`, contacts/reminders CSV, 5 templates, `data_loader.py` | `feat: add dummy contacts and reminders data`<br>`feat: add 5 email templates`<br>`feat: CSV loader with validation` | `02_contacts_csv.png`, `03_email_template.png` |
| 3: Personalisation | `template_engine.py`, `email_sender.py` with dry-run | `feat: template personalisation engine`<br>`feat: SMTP sender with dry-run previews` | `.eml` preview screenshot |
| 4: Scheduling | `reminder_processor.py`, `scheduler.py`, `main.py` CLI | `feat: due-reminder processing with error handling`<br>`feat: add schedule-based reminder loop`<br>`feat: command line interface` | `05_schedule_output.png`, `06_scheduler_running.png` |
| 5: Logs & reports | `report.py`, sent/failed logs, optional dashboard | `feat: CSV report generation and run summary`<br>`feat: optional Streamlit dashboard` | `04_dry_run_output.png`, `07_sent_failed_logs.png`, `08_report_csv.png`, `09_dashboard.png` |
| 6: Documentation | README, docs, sample outputs, repo topics | `docs: add README with setup and sample output`<br>`docs: add project guide and interview prep`<br>`chore: add sample report and logs` | `10_github_repo.png` |

---

## Screenshots / Outputs Checklist

| # | Capture | How |
|---|---|---|
| 1 | Project folder | VS Code Explorer with all folders expanded |
| 2 | Contacts CSV | Open `data/contacts.csv` in Excel |
| 3 | Email template | `templates/meeting_reminder.txt` in VS Code |
| 4 | Dry-run terminal | `python main.py --all` (show summary box) |
| 5 | Reminder schedule | `python main.py --show` |
| 6 | Scheduler live | `python main.py --generate-sample` then `python main.py --schedule --minutes 4`; capture when a WAITING reminder gets sent |
| 7 | Sent/failed logs | `logs/sent.log` and `logs/failed.log` side by side |
| 8 | Report CSV | `outputs/report_*.csv` in Excel, with the FAILED rows visible |
| 9 | Dashboard (optional) | `streamlit run dashboard.py` |
| 10 | GitHub repo | Repo page showing README, topics and commit history |

Windows shortcut: **Win + Shift + S** for snipping. Crop to the relevant area.
