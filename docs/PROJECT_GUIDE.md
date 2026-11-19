# Project Guide: Email Automation & Reminder System

## 1. Project Explanation

### What is it?
**Simple:** A program that sends the right reminder email to the right person at the right time, without anyone typing it.

**Technical:** A Python batch-and-schedule pipeline. It loads structured contact and reminder data (CSV → pandas DataFrames), joins them on `contact_id`, picks reminders whose `send_at` time has arrived, renders a text template with each recipient's details, sends it as a MIME message over an authenticated, TLS-encrypted SMTP session, and records each outcome in logs and a CSV report.

### What problem does it solve?
- Repetitive manual emails waste hours every week
- People forget or send late, which leads to missed meetings and late payments
- Copy-paste mistakes (wrong name, wrong date)
- No record of who was reminded and whether it worked

### Who uses this kind of system
| Team | Example |
|---|---|
| Companies (general) | Meeting alerts, policy deadlines |
| Trainers / EdTech | Class and webinar reminders with join links |
| HR | Interview slots, onboarding documents, appraisal deadlines |
| Sales | Follow-up 2 days after a demo, proposal reminders |
| Finance | Invoice due in 3 days, overdue notices |
| Operations / Admin | Renewals, maintenance, task assignment notifications |

In industry, this logic sits inside CRMs (HubSpot, Salesforce), marketing tools (Mailchimp), calendar apps and ticketing systems. Those tools all follow the same pipeline this project builds.

### How Python automates repetitive communication
- `pandas` reads hundreds of rows from Excel/CSV in one line
- String templates turn one message into hundreds of personalised ones
- `smtplib` talks to any mail server (Gmail, Outlook, company SMTP)
- `schedule` / cron runs the job at the right time with no human involved
- `logging` + CSV give managers an audit trail

### Workflow
```
 contact list  →  message template  →  scheduled reminder  →  email sending  →  status tracking  →  report generation
 contacts.csv     templates/*.txt       reminders.csv           smtplib / dry-run   sent.log / failed.log   outputs/report_*.csv
                                        send_at <= now?
```

---

## 2. Tech Stack Options

| | Option A: Easy | Option B: Intermediate ✅ | Option C: Advanced |
|---|---|---|---|
| Tools | Python, `csv`, `smtplib`, `time.sleep` | Python, **pandas**, `smtplib`, `email.message`, **schedule**, `datetime`, `logging`, `python-dotenv`, Streamlit (optional) | Flask/FastAPI, SQLite/PostgreSQL, Celery + Redis or APScheduler, Jinja2 HTML emails, Docker, SendGrid API |
| Difficulty | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Output | Single script that sends emails from a CSV | Modular project: scheduling, dry-run, logs, CSV reports, dashboard | Web app with database, queue workers and REST API |
| Time | 1 day | 5–6 days | 3–4 weeks |

**Chosen: Option B.** It is realistic enough to discuss in interviews (modular code, scheduling, logging, secrets, reports), it only uses libraries a Python course covers, and it can be extended to Option C later.

---

## 3. Architecture

```
┌────────────────────────── INPUT ──────────────────────────┐
│  data/contacts.csv     data/reminders.csv     templates/   │
└──────────┬───────────────────┬──────────────────┬──────────┘
           │                   │                  │
           ▼                   ▼                  │
   ┌───────────────── data_loader.py ──────────┐  │
   │ read CSV → validate columns → parse dates │  │
   │ LEFT JOIN reminders + contacts            │  │
   └───────────────────┬───────────────────────┘  │
                       ▼                          │
   ┌────────── scheduler.py / main.py ─────────┐  │
   │ every N sec: pick rows where send_at<=now │  │
   │ and not already processed                 │  │
   └───────────────────┬───────────────────────┘  │
                       ▼                          ▼
   ┌──────────── reminder_processor.py ────────────────────┐
   │ validate row → template_engine.render() → personalise │
   └───────────────────┬───────────────────────────────────┘
                       ▼
   ┌────────────── email_sender.py ──────────────┐
   │ DRY-RUN → save .eml preview                 │
   │ LIVE    → SMTP + STARTTLS + login → send    │
   └───────┬───────────────────────────┬─────────┘
           ▼ success                   ▼ exception
     status = SENT/DRY_RUN       status = FAILED + error
           └─────────────┬─────────────┘
                         ▼
┌────────────────────────── OUTPUT ─────────────────────────┐
│ logs/app.log  logs/sent.log  logs/failed.log               │
│ outputs/report_<time>.csv  outputs/report_history.csv      │
│ outputs/dry_run_emails/*.eml   (optional) Streamlit view   │
└────────────────────────────────────────────────────────────┘
```

### Data flow
1. **Load:** two CSVs become DataFrames; dates become `datetime` (bad dates become `NaT` instead of crashing).
2. **Merge:** each reminder gets its contact's name/email. Unknown contacts keep blank fields so they show up as failures.
3. **Filter:** only reminders with `send_at <= now` that haven't been processed run.
4. **Personalise:** the template named in the row is filled with that row's values.
5. **Send:** dry-run writes a preview file; live mode sends over SMTP.
6. **Track:** every row gets a status (`DRY_RUN`, `SENT`, `FAILED`) and an error message if needed.
7. **Report:** results are written to a CSV and summarised in the terminal.

---

## 4. Implementation Plan

| Phase | What to do | Why | Expected output | Common beginner mistakes |
|---|---|---|---|---|
| 1. Setup | Install Python 3.9+, VS Code, Git. Create a venv. | Isolated, repeatable environment | `python --version` works, venv active | Installing packages globally; forgetting to activate the venv |
| 2. Folders | Create `data/ templates/ src/ outputs/ logs/ images/ docs/` | Separating concerns looks professional | Empty structure + `main.py` | Putting everything in one 500-line file |
| 3. Contact CSV | `contacts.csv` with `contact_id,name,email,department,role` | Data separate from code | 10 dummy contacts | Real people's emails; spaces in headers; Excel saving as `.xlsx` |
| 4. Templates | `.txt` files, first line `Subject:` | Non-programmers can edit text | 5 templates | Placeholder typos like `{frist_name}` |
| 5. SMTP config | `.env` + `config.py` reading `os.getenv` | Never hard-code passwords | `smtp_is_configured()` returns True | Using normal Gmail password instead of App Password; committing `.env` |
| 6. Personalisation | `template_engine.render()` with `format_map` | One template, many people | Correct name/date in each email | Crash on missing key (fixed with `SafeDict`) |
| 7. Scheduling | `send_at` column + `schedule.every(N).seconds` | Send at the right time automatically | Waiting reminders get sent once due | Sending the same reminder twice (fixed with `already_done` set) |
| 8. Sending | `EmailSender` with dry-run + live | Safe testing first | `.eml` previews / real emails | Opening a new SMTP login per email; no try/except |
| 9. Logs & reports | `logging` + pandas `to_csv` | Proof and audit trail | `sent.log`, `failed.log`, `report_*.csv` | Only using `print()` with no record kept |
| 10. GitHub | `.gitignore`, README, screenshots, push | Proof of work | Public repo | Uploading `venv/` or `.env` |

---

## 5. Folder Explanation

| Folder / file | Purpose |
|---|---|
| `data/` | Input CSVs (contacts, reminders). Dummy data only. |
| `templates/` | Plain-text email templates; anyone can edit wording without touching code |
| `src/` | All Python modules, one job per file |
| `outputs/` | Generated CSV reports and dry-run `.eml` previews |
| `logs/` | `app.log` (everything), `sent.log`, `failed.log` |
| `images/` | Screenshots used in README |
| `docs/` | This guide, GitHub guide, interview prep |
| `main.py` | Command-line entry point (`--all`, `--schedule`, `--live` …) |
| `dashboard.py` | Optional Streamlit dashboard |
| `requirements.txt` | Libraries to install |
| `.env.example` | Shows which secrets are needed, with no real values |
| `.gitignore` | Keeps `.env`, `venv/`, caches out of Git |

---

## 6. Installation Guide

**Python:** download 3.9+ from python.org. On Windows, tick **"Add Python to PATH"** during install.

**Windows**
```powershell
cd Email-Automation-Reminder-System
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# optional dashboard
pip install streamlit
```
If activation is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (run once).

**Mac / Linux**
```bash
cd Email-Automation-Reminder-System
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Check it: `python -c "import pandas, schedule, dotenv; print('ready')"`

---

## 8. Virtual Simulation (safe testing)

| Step | How |
|---|---|
| Dummy contacts | `python main.py --generate-sample`. Uses `example.com`/`example.org`, domains reserved for testing that can never reach a real inbox. |
| Sample reminders | The same command creates 12 reminders with times **relative to now**: 7 already due, 3 due in 1–3 min, 2 in the future. Two contain deliberate errors (invalid email, unknown contact). |
| Templates | Edit any `templates/*.txt`; keep `Subject:` on line 1. |
| Dry-run | Default mode. `python main.py --all`. Nothing is sent. |
| Inspect emails | Open `outputs/dry_run_emails/R001.eml` (double-click opens in Outlook/Mail, or view in VS Code). |
| Test scheduling | `python main.py --schedule --minutes 4` and watch R006, R008 and R010 get sent as their times arrive. |
| Logs & reports | `logs/sent.log`, `logs/failed.log`, `outputs/report_*.csv`. |
| Safe live test | Put **your own** email in one contact row, set up `.env`, run `python main.py --live`. |

### How it would work in a real company
- Contacts come from an HRMS / CRM export or database instead of a CSV
- SMTP host is the company mail server, or a service like SendGrid / Amazon SES
- The scheduler runs on a server via cron or Windows Task Scheduler (`python main.py` every 5 minutes)
- Reports are emailed to a manager or loaded into a dashboard
- Compliance: unsubscribe links, rate limits and data-privacy rules apply

### What to upload / what NOT to upload
✅ Upload: code, templates, dummy CSVs, one sample report CSV, sample logs (rename to `logs/sample_app.log` etc.), screenshots
❌ Never upload: `.env`, passwords, app passwords, real contact lists, `venv/`, real recipients' emails in screenshots

---

## 9. How to Run & Expected Output

| Command | What happens | Files produced |
|---|---|---|
| `python main.py --generate-sample` | Fresh dummy data | `data/contacts.csv`, `data/reminders.csv` |
| `python main.py --show` | Prints schedule table with DUE/WAITING | none |
| `python main.py` | Dry-run of reminders due now | `.eml` previews, logs, `report_*.csv` |
| `python main.py --all` | Dry-run of every reminder | same |
| `python main.py --schedule` | Checks every 30 s until Ctrl+C | new report each time something is sent |
| `python main.py --live` | Real SMTP send after typing `yes` | logs + report with status `SENT` |

Sample log line (`logs/sent.log`):
```
2026-11-19 21:31:04 | INFO    | R001 | aarav.sharma@example.com | Reminder: Quarterly Sales Review on 19 Nov 2026 at 11:31 PM | DRY_RUN
```
Sample `logs/failed.log`:
```
2026-11-19 21:31:04 | INFO    | R007 | vikram.singh@example | Invalid email address 'vikram.singh@example'
2026-11-19 21:31:04 | INFO    | R009 | ? | Unknown contact_id 'C099'
```
