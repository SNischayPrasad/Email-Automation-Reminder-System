# Interview Preparation

## HR-friendly explanation (non-technical, ~30 seconds)
> "I built a tool that automatically sends reminder emails, like meeting alerts, payment reminders and webinar links, to the right people at the right time. You give it a contact list and a list of reminders in Excel/CSV format, and it personalises each message, sends it when it's due, and produces a report of what was sent and what failed. It saves teams like HR, sales and finance hours of repetitive work, and nobody forgets a follow-up."

## Technical explanation (~60 seconds)
> "It's a modular Python pipeline. pandas loads contacts and reminders from CSV, validates the columns, parses dates and left-joins them on contact_id. A scheduler built on the `schedule` library checks every 30 seconds for reminders whose send_at time has passed, and a set of processed IDs prevents duplicates. Each row is rendered through a text template using `str.format_map` with a safe dictionary, built into an `EmailMessage`, and sent over one reused SMTP connection secured with STARTTLS. Credentials come from environment variables via python-dotenv. Dry-run is the default, so emails are written as .eml previews instead. Every row is wrapped in try/except so one bad record is logged as FAILED without stopping the batch. Results go to separate sent/failed logs and a timestamped CSV report."

---

## 10 Questions & Strong Answers

**1. Explain your project.**
"My project is an Email Automation & Reminder System in Python. Teams like HR, sales and finance send the same reminders repeatedly, which is slow and error-prone. My system reads contacts and reminders from CSV files, picks the right template (I have five: meeting, payment, webinar, follow-up and task), personalises it, and sends it automatically when the reminder is due. It's split into modules for loading data, templating, sending, scheduling and reporting. It has a dry-run mode for safe testing, keeps credentials in environment variables, validates data, and logs every success and failure into a CSV report. In my sample run, 12 reminders were processed: the valid ones were sent, and two deliberately bad records, an invalid email and an unknown contact, were caught and reported instead of crashing the program."

**2. Why did you use pandas instead of the csv module?**
"pandas lets me validate columns, parse dates with `to_datetime`, filter due reminders with one boolean expression and join two tables with `merge`, like SQL. With the csv module I'd have to write loops for all of that. It also makes writing reports one line: `to_csv`."

**3. How do you keep the password secure?**
"It's never in the code. `config.py` reads `SMTP_USER` and `SMTP_PASSWORD` from environment variables, loaded from a local `.env` file that's in `.gitignore`. The repo only has `.env.example` with placeholders. For Gmail I use an App Password, not the account password, so it can be revoked on its own. The SMTP connection uses STARTTLS so credentials are encrypted in transit."

**4. What is dry-run mode and why is it important?**
"Dry-run runs the whole pipeline (loading, validation, personalisation, logging, reporting) but instead of sending, it saves each email as an `.eml` file. It's the default, and live mode needs a `--live` flag plus typing 'yes'. In a company, accidentally emailing 500 clients is a serious incident, so being able to test safely is essential."

**5. How does the scheduling work?**
"Every reminder has a `send_at` time. The `schedule` library runs a job every N seconds that selects rows where `send_at <= now` and the ID isn't in an `already_done` set. That set stops a reminder from being sent twice. In production I'd trigger `main.py` from cron or Windows Task Scheduler and store the status in a database so it survives restarts."

**6. What happens if one email fails?**
"Each reminder is processed inside its own try/except. If validation fails or SMTP raises an error, that row is marked FAILED with the error message, written to `failed.log`, and the loop continues. One bad email address never stops the other 99. The report then shows exactly which ones need attention."

**7. How does personalisation work?**
"Templates are plain text with placeholders like `{first_name}` and `{event_date}`. The first line is the subject. I build a context dictionary from each row and use `str.format_map` with a custom `SafeDict` that returns `{key}` for missing values instead of raising KeyError, so a typo in a template is visible in the preview rather than crashing the run."

**8. Explain how an email is sent with smtplib.**
"I build an `EmailMessage` with From, To, Subject and the body. Then I open `smtplib.SMTP(host, 587)`, call `starttls()` with a default SSL context to encrypt the connection, `login()` with the credentials, and `send_message()`. I open the connection once per batch using a context manager, not once per email, which is faster and less likely to be rate-limited. I also add a small delay between sends."

**9. How would you scale this for a real company?**
"Replace CSVs with a database, use a proper scheduler like APScheduler, Celery or cron, and send through a transactional email service like SendGrid or Amazon SES for deliverability and bounce tracking. I'd add HTML templates with Jinja2, retries with backoff for temporary failures, unsubscribe handling and a web dashboard. The modular design means only the loader and sender need to change."

**10. What challenges did you face?**
"Three main ones. First, sample data with fixed dates went stale, so I wrote a generator that creates reminders relative to the current time. Second, avoiding duplicate sends in the scheduler loop, which I solved with a processed-ID set. Third, deciding what counts as a failure: I added validation for email format and unknown contacts so problems are reported clearly instead of surfacing as SMTP errors."

---

## Bonus quick answers
- **Why modular?** Each file has one job, so it's easier to test, read and replace (e.g. swap SMTP for SendGrid by changing only `email_sender.py`).
- **What's logging vs print?** Logging has levels, timestamps and can write to files, which gives a permanent audit trail.
- **Port 587 vs 465?** 587 starts plain then upgrades with STARTTLS; 465 is SSL from the first byte (`SMTP_SSL`).
- **Which roles does this fit?** Python developer (modular code, libraries), automation (scheduling, error handling), operations/HR/admin (business workflows and reporting).
