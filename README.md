<p align="center">
  <img src="src/fateplanner/ui/assets/app_icon.png" width="150" alt="FatePlanner icon">
</p>

<h1 align="center">FatePlanner</h1>

<p align="center">
  An offline Persian personal planner for tasks, habits, study, finances, goals, and progress.
</p>

<p align="center">
  <strong>فارسی • RTL • Offline • Windows & Linux</strong>
</p>

---

## About

**FatePlanner** is a desktop productivity application designed around a Persian right-to-left experience.

It combines everyday planning tools into one private, offline application without requiring an account, cloud service, or internet connection.

Your personal data is stored locally on your computer.

---

## Features

### Tasks & Planning

- Daily task planning
- Weekly planner
- Jalali calendar
- Task priorities and descriptions
- Start and end times
- Subtasks
- Recurring tasks
- Recurring-task exceptions
- Central Task Center
- Daily progress tracking

### Habits

- Daily habits
- Selected weekday schedules
- Habit completion history
- Current and best streaks
- Jalali monthly habit view
- Progress statistics

### Study Planner

- Study subjects
- Planned study sessions
- Focus timer
- Pomodoro workflow
- Planned vs actual study time
- Study history
- Study analytics

### Personal Finance

- Income and expense tracking
- Custom finance categories
- Monthly category budgets
- Budget progress
- Savings goals
- Deposits and withdrawals
- Savings history

### Analytics

- Task completion statistics
- Habit performance
- Study progress
- Financial summaries
- Expense composition
- Savings progress
- Visual charts and dashboards

### Backup & Data

- Automatic backups
- Manual backups
- Backup restore
- JSON export
- CSV export
- Local SQLite database

### Interface

- Persian-first interface
- Right-to-left layout
- Jalali dates
- Light theme
- Dark theme
- System theme
- Responsive desktop layout
- Windows and Linux support

---

## Privacy

FatePlanner is designed to work completely offline during normal use.

It does not require:

- An account
- Cloud synchronization
- Telemetry
- Analytics services
- External APIs

Tasks, habits, study records, and financial information remain on your computer unless you explicitly export or back them up elsewhere.

---

## Platforms

FatePlanner is being prepared for:

- Windows 10 / 11
- Linux

Pre-built versions will be available from the GitHub Releases page.

---

## Run From Source

### Requirements

- Python 3.11+
- Git

Clone FatePlanner:

```bash
git clone https://github.com/ariyabrave/FatePlanner.git
cd FatePlanner
````

Create a virtual environment:

```bash
python -m venv .venv
```

### Linux

Activate the environment:

```bash
source .venv/bin/activate
```

### Windows PowerShell

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

Install FatePlanner:

```bash
python -m pip install -e ".[dev]"
```

Run:

```bash
fateplanner
```

Run tests:

```bash
pytest -v
```

---

## Local Data

FatePlanner stores user data outside the application installation directory.

### Linux

```text
~/.local/share/FatePlanner/
```

### Windows

```text
%APPDATA%\FatePlanner\
```

The primary database is:

```text
fateplanner.db
```

Automatic backups are stored inside the FatePlanner data directory.

This means application upgrades can replace the program files without replacing your personal planner database.

---

## Technology

FatePlanner is built with:

* Python
* PySide6 / Qt
* SQLite
* jdatetime
* pytest
* PyInstaller

---

## Project Structure

```text
src/fateplanner/
├── database/
├── services/
├── ui/
│   └── assets/
├── utils/
├── resources.py
└── main.py
```

---

## Releases

Official downloads will be published through GitHub Releases:

[https://github.com/ariyabrave/FatePlanner/releases](https://github.com/ariyabrave/FatePlanner/releases)

Please download FatePlanner only from the official repository and release page.

Planned downloadable packages include:

```text
FatePlanner-Windows-Setup.exe
FatePlanner-Windows-Portable.zip
FatePlanner-Linux-x86_64.tar.gz
```

---

## Development Status

FatePlanner is approaching its first public release.

Current release target:

```text
v0.1.0
```

Windows and Linux packaging, installation, and release automation are currently being prepared.

---

## Contributing

Bug reports and suggestions can be submitted through GitHub Issues.

---

## License

A project license will be selected before the first public release.

---

<p align="center">
  Made for a calmer, more organized everyday life.
</p>
