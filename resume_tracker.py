import json
import os
import random
import subprocess
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
JOB_LOG   = os.path.join(BASE, "job_log.json")
CONFIG    = os.path.join(BASE, "tracker_config.json")
GOAL      = 25
SCAN_LOG  = os.path.join(BASE, "scanned_files.json")

# Keywords to classify role from filename (checked in order)
ROLE_KEYWORDS = {
    "da": ["data_analyst", "dataanalyst", "labour_model", "labourmodel",
           "data_transformation_analyst", "excel_data"],
    "ds": ["data_scientist", "datascientist", "data_science", "datascience",
           "ds_ai", "_ds_", "quant_research", "quant_analyst"],
    "ml": ["ml_engineer", "ml_researcher", "ml_scientist", "applied_ml", "founding_ml",
           "deep_learning", "nlp_engineer", "computer_vision"],
    "ai": [
        "ai_engineer", "ai_developer", "ai_devloper", "ai_builder", "ai_specialist",
        "ai_solutions", "ai_creative", "ai_qa", "ai_researcher", "ai_research",
        "ai_platform", "ai_associate", "ai_operations", "ai_data", "applied_ai",
        "agentic_ai", "agenticai", "llm_engineer", "rag_engineer", "graduate_ai",
        "trainee_ai", "aiml_engineer", "forward_deployed_ai", "generative_ai",
        "ml_evaluation", "mle_agentic", "ai_intern", "numi_ai",
        "ai_architect", "ai_software", "ai_security", "ai_product", "ai_strategy",
        "datascience_specialist", "data_science_specialist",
        "software_ai", "founding_ai", "junior_ai", "senior_ai",
        "aiengineer", "aiengineering", "founding_engineer",
    ],
}
MLE_PATTERN = ["_mle", "mle_", "mle."]   # standalone MLE files → ml

ROLES = {
    "ai": "AI / Generative AI Engineer",
    "da": "Data Analyst",
    "ds": "Data Scientist",
    "ml": "Machine Learning Engineer",
}

MOTIVATIONS = [
    "Every application is a vote for your future. Cast 25 votes today!",
    "25 jobs/day = 175/week. Your dream role is in that pile — find it!",
    "You have 4 killer resumes. Each JD is a puzzle — YOU are the answer!",
    "Top candidates don't wait to be discovered — they show up 25 times a day!",
    "Rejection is just redirection. Your YES is out there — keep sending!",
    "The only resume that never gets a call is the one never sent. Send 25!",
    "QLoRA, LangGraph, MLOps, Power BI — companies NEED these skills. Show them!",
    "You're one application away from everything. Don't stop now!",
    "25 applications = 25 chances. More seeds = bigger harvest. Plant them all!",
    "Chase your future — it won't come to you. Get up and APPLY!",
    "Your competition is applying right now. Are you?",
    "Each cover letter is a conversation starter with your next employer. Start 25!",
]

# Each entry: (headline, body, header_color) — 30 unique daily messages
MORNING_MOTIVATIONS = [
    ("Rise & Dominate",               "The job market opens for those who show up first. Today YOU show up 25 times. Let's go, Raju!",                                              "#1a5276"),
    ("Your Breakthrough Day",          "Every great career started with someone who refused to quit. Today could be the day your inbox changes everything.",                          "#145a32"),
    ("25 Shots at Your Dream",         "A sniper takes one shot. A champion takes 25. Load up, aim high — your dream role is hiding in today's batch.",                              "#6e2f8c"),
    ("The Algorithm Favors the Bold",  "Recruiters scroll past ordinary. YOU are QLoRA, LangGraph, MLOps — extraordinary. Apply 25 times and make them stop scrolling.",             "#1a5276"),
    ("Compound Interest on Hustle",    "Each application compounds. Yesterday's seeds, today's opportunities, tomorrow's offers. Plant 25 seeds right now.",                         "#17202a"),
    ("Your Name on an Offer Letter",   "Picture it: your name, a company logo, a life-changing salary. That offer letter starts with one click today. Click 25 times.",              "#145a32"),
    ("The Market Is Waiting for YOU",  "Right now a hiring manager has an open role that fits you perfectly. They just haven't seen your resume yet. Send it!",                       "#78281f"),
    ("Data + Determination = Destiny", "You have the data skills. You have the ML chops. All you need is 25 applications between you and your next chapter.",                        "#154360"),
    ("No Cap on Your Potential",       "There's no ceiling on what you can achieve — but there IS a deadline on today. 24 hours. Use them. Apply 25 times.",                         "#1b2631"),
    ("Champions Clock In Early",       "While others sleep in, you're already building your future. That 7 AM energy? Channel it into 25 applications before noon.",                 "#4a235a"),
    ("Your Skills Are Rare",           "AI Engineers with your depth aren't common. Every JD you skip is a company missing out on you. Don't let them miss you!",                    "#1a5276"),
    ("The 7 AM Advantage",             "You started before the world woke up. Keep that edge. Apply early, apply often — 25 applications and own this day!",                         "#145a32"),
    ("Reject the Fear of Rejection",   "Fear of rejection has kept millions from their dream jobs. Not you. Every 'no' is one step closer to YOUR yes. Apply boldly!",               "#78281f"),
    ("Your Resume Is Your Superpower", "You built it. You refined it. Now DEPLOY it — 25 times today — like the engineer you are.",                                                  "#154360"),
    ("Make Today the Turning Point",   "Weeks from now you'll look back at today as the moment things shifted. Or you won't. The difference is 25 applications.",                    "#6e2f8c"),
    ("Stack the Odds in Your Favor",   "Probability is simple: more applications = more chances. Stack the deck. 25 today. Every day. Watch what happens.",                          "#17202a"),
    ("The Compound Effect",            "Day 1: 25 apps. Day 7: 175 apps. Day 30: 750 apps. That's not job hunting — that's a guaranteed offer in the making.",                       "#145a32"),
    ("Your Moment Is Now",             "Not next Monday. Not after the weekend. NOW. This morning. This session. 25 applications — starting in the next 60 seconds.",                "#1b2631"),
    ("Lay 25 Bricks Today",            "Rome wasn't built in a day, but they laid bricks EVERY day. Lay 25 bricks today. Your career castle is rising.",                             "#4a235a"),
    ("Outwork the Doubt",              "That voice saying 'maybe later' has kept more people unemployed than any recession. Silence it with 25 applications — starting now.",        "#78281f"),
    ("You Are the Product",            "Every great product needs marketing. YOU are the product. Today's 25 applications are your marketing campaign. Launch it!",                  "#1a5276"),
    ("Precision + Volume = Victory",   "A great resume (precision) sent 25 times (volume) = interview invites. You have precision. Now add volume. Go!",                             "#154360"),
    ("The Interview Is Already Yours", "Somewhere, a recruiter will read your resume today and hit 'Schedule Interview'. Make sure you sent it. Apply 25 times.",                    "#145a32"),
    ("Experts Never Stop Applying",    "They never stopped applying — even when they were good. Your expertise is real. Your story is compelling. 25 companies need to hear it.",    "#6e2f8c"),
    ("Today's Seeds, Tomorrow's Offers","The math is simple. The discipline is daily. The reward is life-changing. Start now. 25 applications. Let's go.",                           "#17202a"),
    ("Make the Algorithm Work for You","LinkedIn, Indeed, Naukri — they reward active applicants. Signal your activity with 25 applications and watch the algorithm respond.",        "#1b2631"),
    ("Consistency Beats Talent Alone", "Talented people who show up every day beat talented people who don't. You have talent AND consistency. Use both. Apply 25 times.",            "#4a235a"),
    ("Your Future Self Is Watching",   "In 6 months, Future Raju will look back at this very morning. Give him something to be grateful for. Apply 25 times today.",                "#78281f"),
    ("Do the Math",                    "0 applications = 0 chances. 25 applications = 25 chances. The numbers always win. Choose the winning side. Apply now.",                      "#154360"),
    ("Good Morning, Champion",         "The sun rose. So did you. The job market is open. Your skills are sharp. Your goal is 25. Today is YOUR day — own it.",                     "#1a5276"),
]

# ─── Data helpers ────────────────────────────────────────────────────────────

def load_log():
    if os.path.exists(JOB_LOG):
        with open(JOB_LOG, "r") as f:
            return json.load(f)
    return {}

def save_log(data):
    with open(JOB_LOG, "w") as f:
        json.dump(data, f, indent=2)

def load_config():
    cfg = {}
    if os.path.exists(CONFIG):
        with open(CONFIG, "r") as f:
            cfg = json.load(f)
    # GitHub Actions: override with environment variables (secrets)
    for env_key, cfg_key in [
        ("EMAIL_SENDER",   "email_sender"),
        ("EMAIL_PASSWORD", "email_password"),
        ("EMAIL_RECEIVER", "email_receiver"),
        ("GEMINI_API_KEY", "gemini_api_key"),
    ]:
        val = os.environ.get(env_key, "")
        if val:
            cfg[cfg_key] = val
    return cfg

def today():
    return datetime.now().strftime("%Y-%m-%d")

def today_display():
    return datetime.now().strftime("%A, %d %B %Y")

def get_today_data():
    log = load_log()
    entry = log.get(today(), {})
    if isinstance(entry, int):
        entry = {"total": entry, "roles": {}}
    return entry

def get_today_total():
    d = get_today_data()
    return d.get("total", 0)

def add_application(role_key, n=1):
    log  = load_log()
    t    = today()
    if t not in log or isinstance(log[t], int):
        log[t] = {"total": 0, "roles": {r: 0 for r in ROLES}}
    log[t]["total"] = log[t].get("total", 0) + n
    log[t]["roles"][role_key] = log[t]["roles"].get(role_key, 0) + n
    save_log(log)
    return log[t]

def classify_role(filename):
    name = filename.lower().replace("-", "_").replace(" ", "_")
    for role in ("da", "ds", "ai", "ml"):
        for kw in ROLE_KEYWORDS[role]:
            if kw in name:
                return role
    for kw in MLE_PATTERN:
        if kw in name:
            return "ml"
    return "other"

def load_scan_log():
    if os.path.exists(SCAN_LOG):
        with open(SCAN_LOG, "r") as f:
            return json.load(f)
    return {}

def save_scan_log(data):
    with open(SCAN_LOG, "w") as f:
        json.dump(data, f, indent=2)

def add_application_for_date(date_str, role_key, n=1):
    log = load_log()
    if date_str not in log or isinstance(log[date_str], int):
        log[date_str] = {"total": 0, "roles": {r: 0 for r in ROLES}}
    log[date_str]["total"] = log[date_str].get("total", 0) + n
    log[date_str]["roles"][role_key] = log[date_str]["roles"].get(role_key, 0) + n
    save_log(log)

def scan_and_log():
    scan_log  = load_scan_log()
    new_files = []
    unknown   = []

    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for fname in files:
            if not fname.lower().endswith('.docx'):
                continue
            fpath    = os.path.join(root, fname)
            rel_path = os.path.relpath(fpath, BASE)
            if rel_path in scan_log:
                continue

            role = classify_role(fname)
            mtime     = os.path.getmtime(fpath)
            file_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

            scan_log[rel_path] = {"role": role, "date": file_date}

            if role == "other":
                unknown.append(rel_path)
                continue

            add_application_for_date(file_date, role)
            new_files.append((rel_path, role, file_date))

    save_scan_log(scan_log)

    # Summary
    role_counts = {r: 0 for r in ROLES}
    date_counts = {}
    for _, role, date in new_files:
        role_counts[role] += 1
        date_counts[date] = date_counts.get(date, 0) + 1

    print(f"\n{'='*60}")
    print(f"  SCAN COMPLETE — {len(new_files)} new files logged")
    print(f"{'='*60}")
    if new_files:
        print(f"\n  By Role:")
        for key, label in ROLES.items():
            if role_counts[key]:
                print(f"    {label:<35}: {role_counts[key]}")
        print(f"\n  By Date (most recent 5):")
        for date in sorted(date_counts)[-5:]:
            print(f"    {date}: {date_counts[date]} applications")
    if unknown:
        print(f"\n  Other / Unclassified ({len(unknown)}):")
        for p in unknown[:8]:
            print(f"    {os.path.basename(p)}")
        if len(unknown) > 8:
            print(f"    ... and {len(unknown)-8} more (see scanned_files.json for full list)")
    print(f"{'='*60}\n")

    if new_files:
        auto_push_log()
    return new_files

def auto_push_log():
    """Silently commit and push job_log.json so GitHub Actions midday check sees latest data."""
    try:
        subprocess.run(["git", "add", JOB_LOG, SCAN_LOG], capture_output=True, cwd=BASE)
        result = subprocess.run(
            ["git", "commit", "-m", f"log: applications {today()}"],
            capture_output=True, cwd=BASE
        )
        if result.returncode == 0:
            subprocess.run(["git", "push", "origin", "main"], capture_output=True, cwd=BASE)
    except Exception:
        pass

def get_daily_motivation():
    """Returns a consistent but date-unique morning motivation."""
    r = random.Random(today())
    return r.choice(MORNING_MOTIVATIONS)

# ─── Windows toast notification ───────────────────────────────────────────────

def toast(title, message):
    if sys.platform != "win32":
        return
    t = title.replace("'", "`'")
    m = message.replace("'", "`'")
    ps = f"""
Add-Type -AssemblyName System.Windows.Forms
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon    = [System.Drawing.SystemIcons]::Information
$n.Visible = $true
$n.BalloonTipIcon  = 'Info'
$n.BalloonTipTitle = '{t}'
$n.BalloonTipText  = '{m}'
$n.ShowBalloonTip(9000)
Start-Sleep -Seconds 10
$n.Dispose()
"""
    subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "-Command", ps])

# ─── Email builders ───────────────────────────────────────────────────────────

def build_morning_html():
    applied    = get_today_total()
    data       = get_today_data()
    roles_data = data.get("roles", {r: 0 for r in ROLES})
    remaining  = max(0, GOAL - applied)
    llm        = generate_llm_content("morning", applied, roles_data, remaining)

    if llm:
        headline    = llm.get("headline", "Rise and Dominate Today")
        body        = llm.get("body", "")
        strategy    = llm.get("strategy", "")
        affirmation = llm.get("affirmation", "")
        color       = "#1a5276"
    else:
        headline, body, color = get_daily_motivation()
        strategy    = ""
        affirmation = ""

    date_str   = today_display()
    roles_list = "".join(
        f"<li style='margin:6px 0;font-size:14px;color:#2c3e50;'><b>{label}</b></li>"
        for label in ROLES.values()
    )

    strategy_block = f"""
  <!-- Today's Strategy -->
  <tr><td style='padding:0 28px 20px;'>
    <div style='background:#eaf4fb;border-left:5px solid #2980b9;border-radius:8px;padding:18px 20px;'>
      <p style='margin:0 0 8px;font-size:14px;font-weight:bold;color:#1a5276;
                text-transform:uppercase;letter-spacing:1px;'>Today's Strategy</p>
      <p style='margin:0;font-size:14px;color:#2c3e50;line-height:1.7;'>{strategy}</p>
    </div>
  </td></tr>""" if strategy else ""

    affirmation_block = f"""
  <!-- Affirmation -->
  <tr><td style='padding:0 28px 24px;'>
    <div style='background:linear-gradient(135deg,#1a5276,#6e2f8c);border-radius:10px;
                padding:18px 24px;text-align:center;'>
      <p style='margin:0;font-size:15px;font-style:italic;color:#fff;line-height:1.6;'>
        &ldquo;{affirmation}&rdquo;
      </p>
    </div>
  </td></tr>""" if affirmation else ""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset='UTF-8'></head>
<body style='margin:0;padding:0;background:#f0f3f7;font-family:Arial,sans-serif;'>
<table width='100%' cellpadding='0' cellspacing='0'
       style='max-width:600px;margin:30px auto;background:#fff;border-radius:12px;
              overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.12);'>

  <!-- Header -->
  <tr><td style='background:{color};padding:36px 24px;text-align:center;'>
    <p style='color:#aed6f1;margin:0 0 6px;font-size:13px;letter-spacing:2px;text-transform:uppercase;'>
      Good Morning, Raju · {date_str}
    </p>
    <h1 style='color:#fff;margin:0;font-size:26px;line-height:1.3;'>{headline}</h1>
  </td></tr>

  <!-- Motivation body -->
  <tr><td style='padding:28px 28px 16px;'>
    <p style='font-size:16px;color:#2c3e50;line-height:1.8;margin:0;'>{body}</p>
  </td></tr>

  {strategy_block}

  <!-- Daily goal banner -->
  <tr><td style='padding:4px 28px 20px;'>
    <div style='background:linear-gradient(135deg,{color},#2980b9);border-radius:10px;
                padding:20px;text-align:center;'>
      <p style='color:#fff;margin:0;font-size:26px;font-weight:bold;'>TODAY'S GOAL: {GOAL} APPLICATIONS</p>
      <p style='color:#d6eaf8;margin:6px 0 0;font-size:14px;'>Across 4 roles — AI · DA · DS · ML</p>
    </div>
  </td></tr>

  <!-- Role targets -->
  <tr><td style='padding:0 28px 20px;'>
    <p style='margin:0 0 10px;font-size:15px;font-weight:bold;color:#2c3e50;'>Apply across all 4 roles today:</p>
    <ul style='margin:0;padding-left:20px;'>
      {roles_list}
    </ul>
  </td></tr>

  {affirmation_block}

</table>
<p style='text-align:center;font-size:11px;color:#bbb;margin-top:12px;'>
  Job Application Tracker · Baddela Raju · {date_str}
</p>
</body></html>
"""

def build_midday_html(applied, roles_data, label_time="12:00 PM"):
    remaining = max(0, GOAL - applied)
    pct       = min(100, int(applied / GOAL * 100))
    is_goal   = applied >= GOAL
    bar_color = "#27ae60" if is_goal else "#e67e22" if pct >= 50 else "#e74c3c"
    date_str  = today_display()

    # ── Header ──────────────────────────────────────────────
    if is_goal:
        header_bg  = "#145a32"
        header_txt = f"🏆 GOAL CRUSHED — {applied}/{GOAL} by Noon!"
        sub_txt    = "You hit the daily target before noon — extraordinary!"
    elif applied >= 15:
        header_bg  = "#1a5276"
        header_txt = f"🔥 {applied}/{GOAL} Done — Strong Morning!"
        sub_txt    = f"12:00 PM Summary · {date_str}"
    elif applied >= 5:
        header_bg  = "#784212"
        header_txt = f"⚠️ {applied}/{GOAL} Done — Afternoon Push Needed"
        sub_txt    = f"12:00 PM Summary · {date_str}"
    else:
        header_bg  = "#922b21"
        header_txt = f"🚨 {applied}/{GOAL} — Noon Alert!"
        sub_txt    = f"Day is half gone · {date_str}"

    # ── Tiered ending message (hardcoded defaults) ───────────────
    if is_goal:
        end_color = "#27ae60"
        end_icon  = "trophy"
        end_title = "Morning Champion — Goal Achieved!"
        end_body  = (
            f"You applied to <b>{applied} jobs</b> and crushed your daily goal of {GOAL} before noon. "
            "That level of discipline is exactly what separates people who land jobs from people who don't. "
            "Take a short break — you've absolutely earned it. Carry this same energy into tomorrow!"
        )
    elif applied >= 15:
        end_color = "#e67e22"
        end_icon  = "fire"
        end_title = "Great Morning — Finish It This Afternoon!"
        end_body  = (
            f"<b>{applied} applications</b> done — you're on a great track! "
            f"Just <b>{remaining} more</b> to hit your daily goal. "
            "Block one focused hour, power through, and end today knowing you gave it everything."
        )
    elif applied >= 5:
        end_color = "#c0392b"
        end_icon  = "clock"
        end_title = "Push Hard This Afternoon!"
        end_body  = (
            f"You have <b>{applied} applications</b> so far. You need <b>{remaining} more</b> "
            "to hit your goal — close every distraction and apply non-stop for the next 2 hours."
        )
    else:
        end_color = "#922b21"
        end_icon  = "alert"
        end_title = "Urgent — The Clock Is Running. Act NOW!"
        end_body  = (
            f"<b>{'Zero' if applied == 0 else str(applied)} applications</b> so far, Raju. "
            "Your dream job will not find you — you have to chase it. "
            "Set a 60-minute timer and apply to at least 15 jobs right now."
        )

    # ── Override with LLM personalised content if available ──────
    email_kind  = "midnight" if label_time == "12:00 AM" else "check"
    llm         = generate_llm_content(email_kind, applied, roles_data, remaining)
    action_plan = ""
    role_insight= ""
    tomorrow_plan = ""
    strength    = ""
    if llm:
        end_title     = llm.get("headline", end_title)
        end_body      = llm.get("body", end_body)
        action_plan   = llm.get("action_plan", "")
        role_insight  = llm.get("role_insight", "")
        tomorrow_plan = llm.get("tomorrow_plan", "")
        strength      = llm.get("strength", "")

    # ── Pre-build extra LLM blocks (avoids backslash-in-f-string on Python < 3.12) ──
    action_plan_block = (
        "<tr><td style='padding:0 24px 16px;'>"
        "<div style='background:#eafaf1;border-left:5px solid #27ae60;border-radius:8px;padding:18px 20px;'>"
        "<p style='margin:0 0 8px;font-size:13px;font-weight:bold;color:#1e8449;"
        "text-transform:uppercase;letter-spacing:1px;'>Next 2 Hours — Your Action Plan</p>"
        f"<p style='margin:0;font-size:14px;color:#2c3e50;line-height:1.7;'>{action_plan}</p>"
        "</div></td></tr>"
    ) if action_plan else ""

    role_insight_block = (
        "<tr><td style='padding:0 24px 16px;'>"
        "<div style='background:#fef9e7;border-left:5px solid #f39c12;border-radius:8px;padding:16px 20px;'>"
        "<p style='margin:0 0 6px;font-size:13px;font-weight:bold;color:#d68910;"
        "text-transform:uppercase;letter-spacing:1px;'>Role Focus Insight</p>"
        f"<p style='margin:0;font-size:14px;color:#2c3e50;line-height:1.7;'>{role_insight}</p>"
        "</div></td></tr>"
    ) if role_insight else ""

    tomorrow_plan_block = (
        "<tr><td style='padding:0 24px 16px;'>"
        "<div style='background:#eaf4fb;border-left:5px solid #2980b9;border-radius:8px;padding:18px 20px;'>"
        "<p style='margin:0 0 8px;font-size:13px;font-weight:bold;color:#1a5276;"
        "text-transform:uppercase;letter-spacing:1px;'>Tomorrow's Game Plan</p>"
        f"<p style='margin:0;font-size:14px;color:#2c3e50;line-height:1.7;'>{tomorrow_plan}</p>"
        "</div></td></tr>"
    ) if tomorrow_plan else ""

    strength_block = (
        "<tr><td style='padding:0 24px 24px;'>"
        "<div style='background:linear-gradient(135deg,#1a5276,#6e2f8c);border-radius:10px;padding:18px 24px;'>"
        "<p style='margin:0 0 8px;font-size:13px;font-weight:bold;color:#aed6f1;"
        "text-transform:uppercase;letter-spacing:1px;'>Skill to Spotlight Tomorrow</p>"
        f"<p style='margin:0;font-size:14px;color:#fff;line-height:1.7;'>{strength}</p>"
        "</div></td></tr>"
    ) if strength else ""

    # ── Role rows ────────────────────────────────────────────
    roles_rows = ""
    for key, label in ROLES.items():
        count = roles_data.get(key, 0)
        roles_rows += f"""
        <tr>
          <td style='padding:10px 16px;border-bottom:1px solid #eee;'>{label}</td>
          <td style='padding:10px 16px;border-bottom:1px solid #eee;text-align:center;
                     font-weight:bold;color:#2c3e50;'>{count}</td>
        </tr>"""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset='UTF-8'></head>
<body style='margin:0;padding:0;background:#f0f3f7;font-family:Arial,sans-serif;'>
<table width='100%' cellpadding='0' cellspacing='0'
       style='max-width:600px;margin:30px auto;background:#fff;border-radius:12px;
              overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);'>

  <!-- Header -->
  <tr><td style='background:{header_bg};padding:30px 24px;text-align:center;'>
    <p style='color:#aed6f1;margin:0 0 6px;font-size:12px;letter-spacing:2px;text-transform:uppercase;'>
      {label_time} · Daily Summary
    </p>
    <h1 style='color:#fff;margin:0;font-size:22px;'>{header_txt}</h1>
    <p style='color:#aed6f1;margin:8px 0 0;font-size:14px;'>{sub_txt}</p>
  </td></tr>

  <!-- Progress bar -->
  <tr><td style='padding:24px 24px 10px;'>
    <p style='margin:0 0 8px;font-size:14px;color:#7f8c8d;'>Daily Progress</p>
    <div style='background:#ecf0f1;border-radius:50px;height:22px;overflow:hidden;'>
      <div style='width:{pct}%;background:{bar_color};height:100%;border-radius:50px;'></div>
    </div>
    <p style='margin:8px 0 0;font-size:13px;color:{bar_color};font-weight:bold;'>
      {applied}/{GOAL} applied ({pct}%)
      {" — GOAL MET! 🎉" if is_goal else f" — {remaining} more to reach your goal"}
    </p>
  </td></tr>

  <!-- Role breakdown -->
  <tr><td style='padding:10px 24px 20px;'>
    <p style='margin:0 0 10px;font-size:15px;font-weight:bold;color:#2c3e50;'>Applications by Role</p>
    <table width='100%' style='border-collapse:collapse;border-radius:8px;overflow:hidden;border:1px solid #eee;'>
      <tr style='background:#2c3e50;'>
        <th style='padding:10px 16px;color:#fff;text-align:left;font-size:13px;'>Role</th>
        <th style='padding:10px 16px;color:#fff;text-align:center;font-size:13px;'>Applied</th>
      </tr>
      {roles_rows}
      <tr style='background:#f0f3f7;'>
        <td style='padding:12px 16px;font-weight:bold;color:#2c3e50;font-size:14px;'>Total</td>
        <td style='padding:12px 16px;text-align:center;font-weight:bold;font-size:20px;color:{bar_color};'>{applied}</td>
      </tr>
    </table>
  </td></tr>

  <!-- Ending message -->
  <tr><td style='padding:4px 24px 16px;'>
    <div style='background:{end_color}18;border-left:5px solid {end_color};
                border-radius:8px;padding:22px;'>
      <p style='margin:0 0 10px;font-size:19px;font-weight:bold;color:{end_color};'>
        {end_icon} {end_title}
      </p>
      <p style='margin:0;font-size:15px;color:#2c3e50;line-height:1.8;'>
        {end_body}
      </p>
    </div>
  </td></tr>

  {action_plan_block}
  {role_insight_block}
  {tomorrow_plan_block}
  {strength_block}

</table>
<p style='text-align:center;font-size:11px;color:#bbb;margin-top:12px;'>
  Job Application Tracker · Baddela Raju · {date_str}
</p>
</body></html>
"""

def build_html(applied, goal, roles_data, is_goal_met):
    remaining = max(0, goal - applied)
    pct        = min(100, int(applied / goal * 100))
    bar_color  = "#27ae60" if is_goal_met else "#e67e22" if pct >= 50 else "#e74c3c"
    motivation = random.choice(MOTIVATIONS)
    now_str    = datetime.now().strftime("%I:%M %p")
    date_str   = today_display()

    if is_goal_met:
        header_bg  = "#1a5276"
        header_txt = f"🎉 GOAL CRUSHED — {applied}/{goal} Applications Today!"
        sub_txt    = "You're an absolute machine. Your dream job is getting closer!"
        cta        = "<p style='font-size:18px;color:#27ae60;font-weight:bold;'>🏆 OUTSTANDING WORK TODAY! Keep this momentum tomorrow!</p>"
    elif applied == 0:
        header_bg  = "#922b21"
        header_txt = f"⚠️ 0/{goal} Applications — Day Not Started!"
        sub_txt    = "Get started RIGHT NOW. Every hour counts!"
        cta        = f"<p style='font-size:16px;color:#e74c3c;font-weight:bold;'>🔥 {motivation}</p>"
    else:
        header_bg  = "#1a5276"
        header_txt = f"📋 {applied}/{goal} Applications Today — {remaining} More Needed!"
        sub_txt    = f"As of {now_str} on {date_str}"
        cta        = f"<p style='font-size:15px;color:#e67e22;font-weight:bold;'>💪 {motivation}</p>"

    roles_rows = ""
    for key, label in ROLES.items():
        count = roles_data.get(key, 0)
        roles_rows += f"""
        <tr>
          <td style='padding:10px 16px;border-bottom:1px solid #eee;'>{label}</td>
          <td style='padding:10px 16px;border-bottom:1px solid #eee;text-align:center;font-weight:bold;color:#2c3e50;'>{count}</td>
        </tr>"""

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset='UTF-8'></head>
<body style='margin:0;padding:0;background:#f0f3f7;font-family:Arial,sans-serif;'>
<table width='100%' cellpadding='0' cellspacing='0' style='max-width:600px;margin:30px auto;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);'>

  <!-- Header -->
  <tr><td style='background:{header_bg};padding:30px 24px;text-align:center;'>
    <h1 style='color:#fff;margin:0;font-size:22px;'>{header_txt}</h1>
    <p style='color:#aed6f1;margin:8px 0 0;font-size:14px;'>{sub_txt}</p>
  </td></tr>

  <!-- Progress bar -->
  <tr><td style='padding:24px 24px 10px;'>
    <p style='margin:0 0 8px;font-size:14px;color:#7f8c8d;'>Daily Progress</p>
    <div style='background:#ecf0f1;border-radius:50px;height:22px;overflow:hidden;'>
      <div style='width:{pct}%;background:{bar_color};height:100%;border-radius:50px;transition:width 0.5s;'></div>
    </div>
    <p style='margin:8px 0 0;font-size:13px;color:{bar_color};font-weight:bold;'>{applied}/{goal} applied &nbsp;({pct}%){" — GOAL MET! 🎉" if is_goal_met else f" — {remaining} more to go"}</p>
  </td></tr>

  <!-- Role breakdown -->
  <tr><td style='padding:10px 24px 20px;'>
    <p style='margin:0 0 10px;font-size:15px;font-weight:bold;color:#2c3e50;'>Applications by Role</p>
    <table width='100%' style='border-collapse:collapse;border-radius:8px;overflow:hidden;border:1px solid #eee;'>
      <tr style='background:#2c3e50;'>
        <th style='padding:10px 16px;color:#fff;text-align:left;font-size:13px;'>Role</th>
        <th style='padding:10px 16px;color:#fff;text-align:center;font-size:13px;'>Applied</th>
      </tr>
      {roles_rows}
    </table>
  </td></tr>

  <!-- CTA / Motivation -->
  <tr><td style='padding:0 24px 20px;text-align:center;'>
    {cta}
  </td></tr>

</table>
<p style='text-align:center;font-size:11px;color:#bbb;margin-top:12px;'>Job Application Tracker · Baddela Raju · {date_str}</p>
</body></html>
"""

# ─── Email sender ─────────────────────────────────────────────────────────────

def send_email_raw(subject, html_body):
    cfg      = load_config()
    sender   = cfg.get("email_sender", "")
    password = cfg.get("email_password", "")
    receiver = cfg.get("email_receiver", "rajubaddela1234@gmail.com")

    if not sender or not password:
        print("Email not configured. Run: python resume_tracker.py setup")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = receiver
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
            srv.login(sender, password)
            srv.sendmail(sender, receiver, msg.as_string())
        print(f"Email sent to {receiver}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

def send_email(subject, applied, roles_data, is_goal_met):
    html = build_html(applied, GOAL, roles_data, is_goal_met)
    send_email_raw(subject, html)

# ─── 7 AM — Morning motivation ────────────────────────────────────────────────

def morning_motivate():
    headline, body, _ = get_daily_motivation()
    date_str  = today_display()
    subject   = f"🌅 Good Morning, Raju! — {headline} | {date_str}"

    toast(
        f"Good Morning! {headline}",
        f"{body[:120]}... Goal: {GOAL} applications today!"
    )
    html = build_morning_html()
    send_email_raw(subject, html)

    print(f"\n{'='*55}")
    print(f"  7 AM MORNING MOTIVATION")
    print(f"  {date_str}")
    print(f"  Headline : {headline}")
    print(f"  Goal     : {GOAL} applications today")
    print(f"  Roles    : AI | DA | DS | ML")
    print(f"{'='*55}\n")

# ─── 12 PM — Midday check ────────────────────────────────────────────────────

def midday_check():
    data       = get_today_data()
    applied    = data.get("total", 0)
    roles_data = data.get("roles", {r: 0 for r in ROLES})
    remaining  = GOAL - applied
    is_goal    = applied >= GOAL
    date_str   = today_display()

    if is_goal:
        subject = f"🏆 Midday — GOAL MET! {applied}/{GOAL} Applications | {date_str}"
        t_title = f"Midday Check: GOAL MET — {applied}/{GOAL}!"
        t_msg   = "You crushed the goal before noon! Outstanding work today, Raju!"
    elif applied == 0:
        subject = f"⚠️ Midday Alert — 0/{GOAL} Applications Yet! | {date_str}"
        t_title = "Midday Alert: 0 Applications!"
        t_msg   = f"It's noon and you haven't started! {GOAL} applications needed — go NOW!"
    else:
        subject = f"📊 12 PM Check — {applied}/{GOAL} Done, {remaining} More Needed | {date_str}"
        t_title = f"Midday: {applied}/{GOAL} Applications"
        t_msg   = (f"{applied} done, {remaining} to go this afternoon! "
                   f"AI={roles_data.get('ai',0)} DA={roles_data.get('da',0)} "
                   f"DS={roles_data.get('ds',0)} ML={roles_data.get('ml',0)}")

    toast(t_title, t_msg)
    html = build_midday_html(applied, roles_data)
    send_email_raw(subject, html)

    print(f"\n{'='*55}")
    print(f"  12 PM MIDDAY CHECK")
    print(f"  Date    : {date_str}")
    print(f"  Applied : {applied}/{GOAL}")
    print(f"  Status  : {'GOAL MET!' if is_goal else f'{remaining} remaining this afternoon'}")
    print(f"  AI Eng  : {roles_data.get('ai', 0)}")
    print(f"  Data Ana: {roles_data.get('da', 0)}")
    print(f"  Data Sci: {roles_data.get('ds', 0)}")
    print(f"  ML Eng  : {roles_data.get('ml', 0)}")
    print(f"{'='*55}\n")

# ─── 12 AM — Midnight final summary ──────────────────────────────────────────

def midnight_summary():
    data       = get_today_data()
    applied    = data.get("total", 0)
    roles_data = data.get("roles", {r: 0 for r in ROLES})
    remaining  = GOAL - applied
    is_goal    = applied >= GOAL
    date_str   = today_display()

    if is_goal:
        subject = f"🏆 Day Complete — GOAL CRUSHED! {applied}/{GOAL} Applications | {date_str}"
        t_title = f"Day Done: GOAL CRUSHED — {applied}/{GOAL}!"
        t_msg   = "You finished the day strong! Outstanding work, Raju!"
    elif applied >= 15:
        subject = f"🔥 Day Wrap-Up — {applied}/{GOAL} Applications | {date_str}"
        t_title = f"Day Done: {applied}/{GOAL} — Great effort!"
        t_msg   = f"{applied} applications today. {remaining} short of goal — push harder tomorrow!"
    elif applied >= 5:
        subject = f"⚠️ Day Wrap-Up — {applied}/{GOAL} Applications | {date_str}"
        t_title = f"Day Done: {applied}/{GOAL} — Need more tomorrow"
        t_msg   = f"Only {applied} applications today. Tomorrow: start early, apply harder!"
    else:
        subject = f"🚨 Day Wrap-Up — Only {applied}/{GOAL} Applications | {date_str}"
        t_title = f"Day Done: {applied}/{GOAL} — Not enough!"
        t_msg   = f"{'Zero' if applied == 0 else applied} applications today. Tomorrow is a fresh start — make it count!"

    toast(t_title, t_msg)
    html = build_midday_html(applied, roles_data, label_time="12:00 AM")
    send_email_raw(subject, html)

    print(f"\n{'='*55}")
    print(f"  12 AM MIDNIGHT FINAL SUMMARY")
    print(f"  Date    : {date_str}")
    print(f"  Applied : {applied}/{GOAL}")
    print(f"  Status  : {'GOAL MET!' if is_goal else f'{remaining} short of goal'}")
    print(f"  AI Eng  : {roles_data.get('ai', 0)}")
    print(f"  Data Ana: {roles_data.get('da', 0)}")
    print(f"  Data Sci: {roles_data.get('ds', 0)}")
    print(f"  ML Eng  : {roles_data.get('ml', 0)}")
    print(f"{'='*55}\n")

# ─── Core check ───────────────────────────────────────────────────────────────

def check_and_notify():
    data      = get_today_data()
    applied   = data.get("total", 0)
    roles_data = data.get("roles", {r: 0 for r in ROLES})
    remaining = GOAL - applied
    is_goal   = applied >= GOAL
    hour      = datetime.now().hour

    if is_goal:
        title   = f"GOAL CRUSHED! {applied}/{GOAL} Jobs Applied Today!"
        message = "You're unstoppable! 25+ applications done. Keep the momentum tomorrow!"
        subject = f"🏆 GOAL ACHIEVED — {applied}/{GOAL} Applications | {today_display()}"
    elif applied == 0 and hour >= 10:
        title   = "URGENT: 0 Applications Yet Today!"
        message = f"You haven't started! 0/{GOAL} jobs applied. Get going NOW — {random.choice(MOTIVATIONS)}"
        subject = f"⚠️ 0/{GOAL} Applications Today — Start NOW! | {today_display()}"
    elif applied == 0:
        title   = f"Good Morning! Time to Apply — Goal: {GOAL} Jobs Today"
        message = f"Start your day strong! Apply to {GOAL} jobs across 4 roles. {random.choice(MOTIVATIONS)}"
        subject = f"🌅 Morning Push — 0/{GOAL} Applications | {today_display()}"
    else:
        title   = f"Job Tracker: {applied}/{GOAL} Applied — {remaining} More Needed!"
        message = f"{applied} done, {remaining} to go! Roles: AI={roles_data.get('ai',0)} | DA={roles_data.get('da',0)} | DS={roles_data.get('ds',0)} | ML={roles_data.get('ml',0)}"
        subject = f"📋 {applied}/{GOAL} Applications Today — {remaining} More To Go! | {today_display()}"

    toast(title, message)
    send_email(subject, applied, roles_data, is_goal)
    print(f"\n{'='*50}")
    print(f"  Date    : {today_display()}")
    print(f"  Applied : {applied}/{GOAL}")
    print(f"  Status  : {'GOAL MET!' if is_goal else f'{remaining} remaining'}")
    print(f"  AI Eng  : {roles_data.get('ai',0)}")
    print(f"  Data Ana: {roles_data.get('da',0)}")
    print(f"  Data Sci: {roles_data.get('ds',0)}")
    print(f"  ML Eng  : {roles_data.get('ml',0)}")
    print(f"{'='*50}\n")

# ─── Summary ──────────────────────────────────────────────────────────────────

def show_summary():
    log = load_log()
    print(f"\n{'='*65}")
    print(f"  JOB APPLICATION TRACKER — BADDELA RAJU")
    print(f"{'='*65}")
    if not log:
        print("  No data yet. Start logging with: python resume_tracker.py add ai 3")
        return
    grand_total = 0
    goal_days   = 0
    role_totals = {r: 0 for r in ROLES}
    for date in sorted(log):
        entry = log[date]
        if isinstance(entry, int):
            total = entry
            roles = {}
        else:
            total = entry.get("total", 0)
            roles = entry.get("roles", {})
        grand_total += total
        status = "✅ GOAL" if total >= GOAL else f"❌ MISSED (-{GOAL - total})"
        if total >= GOAL:
            goal_days += 1
        role_str = f"AI={roles.get('ai',0)} DA={roles.get('da',0)} DS={roles.get('ds',0)} ML={roles.get('ml',0)}"
        print(f"  {date}  {total:3d}/{GOAL}  [{status}]  {role_str}")
        for r in ROLES:
            role_totals[r] += roles.get(r, 0)
    print(f"{'─'*65}")
    print(f"  Total applications  : {grand_total}")
    print(f"  Days tracked        : {len(log)}")
    print(f"  Days goal met       : {goal_days}")
    print(f"  Days goal missed    : {len(log) - goal_days}")
    print(f"\n  By Role:")
    for key, label in ROLES.items():
        print(f"    {label:<35}: {role_totals[key]}")
    print(f"{'='*65}\n")

# ─── Setup email ──────────────────────────────────────────────────────────────

def setup_email():
    print("\n=== Email Setup for Job Tracker ===")
    print("You need a Gmail App Password (NOT your regular Gmail password)")
    print("Steps:")
    print("  1. Go to myaccount.google.com > Security > 2-Step Verification (enable it)")
    print("  2. Go to myaccount.google.com > Security > App Passwords")
    print("  3. Create an app password for 'Mail'")
    print("  4. Copy the 16-character password\n")
    sender   = input("Your Gmail address (sender): ").strip()
    password = input("Gmail App Password (16 chars): ").strip()
    receiver = input("Receiver email [rajubaddela1234@gmail.com]: ").strip()
    if not receiver:
        receiver = "rajubaddela1234@gmail.com"
    gemini  = input("Gemini API Key (leave blank to skip): ").strip()
    cfg = {"email_sender": sender, "email_password": password,
           "email_receiver": receiver, "gemini_api_key": gemini}
    with open(CONFIG, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"\nConfig saved to {CONFIG}")
    print("Now run: python resume_tracker.py schedule")
    print("  → to register the 7 AM & 12 PM Windows scheduled tasks.")

# ─── Setup Windows Task Scheduler ────────────────────────────────────────────

def setup_scheduler():
    python = sys.executable
    script = os.path.abspath(__file__)
    # Windows schtasks /tr needs escaped inner quotes around paths with spaces
    tr = f'\\"{python}\\" \\"{script}\\"'

    print(f"\n{'='*60}")
    print("  Setting up Windows Task Scheduler")
    print(f"  Python : {python}")
    print(f"  Script : {script}")
    print(f"{'='*60}\n")

    def register(name, sc_flags, arg, desc):
        cmd = f'schtasks /create /tn "{name}" /tr "{tr} {arg}" {sc_flags} /f'
        r   = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        tag = "[OK]  " if r.returncode == 0 else "[FAIL]"
        print(f"  {tag}  {desc}")
        if r.returncode != 0:
            print(f"         {r.stderr.strip()}")

    # Watcher uses pythonw.exe (no console window) so it runs silently in background
    pythonw = python.replace("python.exe", "pythonw.exe")
    tw = f'\\"{pythonw}\\" \\"{script}\\"'

    register("ResumeTracker_Morning_7AM",     "/sc daily /st 07:00", "morning", "[07:00] 7 AM motivation email")
    register("ResumeTracker_Midday_12PM",     "/sc daily /st 12:00", "midday",  "[12:00] 12 PM progress email")

    # Watcher: starts silently at login, detects new files every 30s
    watch_cmd = f'schtasks /create /tn "ResumeTracker_Watcher" /tr "{tw} watch" /sc onlogon /f'
    r = subprocess.run(watch_cmd, shell=True, capture_output=True, text=True)
    tag = "[OK]  " if r.returncode == 0 else "[FAIL]"
    print(f"  {tag}  [Login ] File watcher starts silently on PC startup (checks every 30s)")
    if r.returncode != 0:
        print(f"         {r.stderr.strip()}")
        print(f"         Run this terminal as Administrator and try again.")

    print(f"\n  How it works:")
    print(f"    - Drop a .docx into any folder under {BASE}")
    print(f"    - Within 30 min (or on next login) it is auto-classified and pushed to GitHub")
    print(f"    - Scheduled emails always show the real count")
    print(f"\n  To remove auto-scan tasks:")
    print(f"    schtasks /delete /tn ResumeTracker_Scan_OnLogin /f")
    print(f"    schtasks /delete /tn ResumeTracker_Scan_Every30Min /f")
    print(f"{'='*60}\n")

# ─── LLM / Gemini integration ─────────────────────────────────────────────────

def load_context():
    path = os.path.join(BASE, "context.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

def get_day_context():
    now  = datetime.now()
    wd   = now.weekday()   # 0=Mon … 6=Sun
    hour = now.hour
    on_shift = (
        (wd == 3 and hour >= 23) or
        (wd == 4 and hour < 11)  or
        (wd == 4 and hour >= 23) or
        (wd == 5 and hour < 11)
    )
    if on_shift:
        return (
            "Raju is currently ON his Amazon Associate night shift (Thu 11PM-Fri 11AM or Fri 11PM-Sat 11AM). "
            "He has very limited time. Even 5-10 quality applications is a great achievement today. "
            "Do NOT pressure him with the full 25-job goal — acknowledge his effort working night shifts while job hunting."
        )
    if wd == 5:
        return "It is Saturday. Recruiter activity is low on weekends — fewer responses expected. Encourage quality over quantity."
    if wd == 6:
        return "It is Sunday. Recruiter activity is very low. Encourage Raju to apply to a few high-quality roles and use time to refine resumes."
    return "Normal weekday — Raju should aim for the full 25 applications today."

def _build_gemini_profile():
    """Build a rich profile string from context.json for the LLM prompt."""
    ctx = load_context()
    if not ctx:
        return ""
    p   = ctx.get("personal", {})
    ws  = ctx.get("work_schedule", {})
    jh  = ctx.get("job_hunt", {})
    res = ctx.get("resumes", {})

    # Collect skills per role
    role_skills = []
    for rkey in ("ai_engineer", "data_analyst", "data_scientist", "ml_engineer"):
        r = res.get(rkey, {})
        if r:
            skills_preview = " | ".join(r.get("skills", [])[:3])
            role_skills.append(f"  [{r.get('title',rkey)}]: {skills_preview}")

    # Collect all projects with metrics
    projects = []
    seen = set()
    for rkey in ("ai_engineer", "ml_engineer", "data_scientist", "data_analyst"):
        for proj in res.get(rkey, {}).get("projects", []):
            name = proj.get("name", "")
            if name not in seen:
                seen.add(name)
                h = proj.get("highlights", [""])
                projects.append(f"  - {name}: {h[0]}")

    # Collect experience
    exp_lines = []
    seen_exp = set()
    for rkey in ("ai_engineer", "ml_engineer"):
        for e in res.get(rkey, {}).get("experience", []):
            key = e.get("company","") + e.get("role","")
            if key not in seen_exp:
                seen_exp.add(key)
                h = " | ".join(e.get("highlights", [])[:2])
                exp_lines.append(f"  - {e.get('company')} ({e.get('role')}, {e.get('period')}): {h}")

    certs = []
    for rkey in res:
        for c in res[rkey].get("certifications", []):
            if c not in certs:
                certs.append(c)

    return f"""=== BADDELA RAJU — FULL PROFILE ===
Personal : {p.get('name')}, {p.get('location')} | {p.get('email')} | {p.get('phone')}
Education: {p.get('education')}
Context  : {p.get('context','')}

Target Roles: {' | '.join(jh.get('target_roles', []))}
Daily Goal  : {jh.get('daily_goal', 25)} applications/day

SKILLS BY ROLE:
{chr(10).join(role_skills)}

WORK EXPERIENCE:
{chr(10).join(exp_lines)}

NOTABLE PROJECTS (with real metrics):
{chr(10).join(projects[:8])}

CERTIFICATIONS: {', '.join(certs[:6])}

AMAZON SHIFT SCHEDULE:
  {' | '.join(ws.get('amazon_shifts', []))}
  Note: {ws.get('shift_note','')}
"""

def generate_llm_content(email_type, applied, roles_data, remaining):
    """Call Gemini to generate rich, detailed personalised email content. Returns dict or None."""
    cfg     = load_config()
    api_key = cfg.get("gemini_api_key", "")
    if not api_key:
        return None

    try:
        from google import genai
        import re as _re
    except ImportError:
        return None

    day_note = get_day_context()
    date_str = today_display()
    profile  = _build_gemini_profile()

    progress = f"""
=== TODAY'S STATUS ===
Date     : {date_str}
Schedule : {day_note}
Progress : {applied}/{GOAL} applications done, {remaining} remaining
  AI / Generative AI Engineer : {roles_data.get('ai', 0)}
  Data Analyst                : {roles_data.get('da', 0)}
  Data Scientist              : {roles_data.get('ds', 0)}
  ML Engineer                 : {roles_data.get('ml', 0)}
"""

    if email_type == "morning":
        instruction = f"""You are Raju's deeply personal AI job hunt coach. Write a MORNING MOTIVATION email.
Use his REAL skills and projects naturally — LangGraph, QLoRA, RAG, MLflow, Power BI, YOLOv8, LSTM etc.
Make him feel his expertise is genuinely rare in London's AI market.
Acknowledge today's schedule context if relevant.

Return ONLY valid JSON — no markdown fences, no extra text:
{{
  "headline": "punchy unique headline 5-8 words capturing today's energy — no emoji",
  "body": "4-5 sentences — energetic personal coach tone, references at least 2 of his specific projects or skills by name, connects his background to real London market demand, makes him excited to open his laptop and apply",
  "strategy": "2-3 sentences — specific tactical advice for today: which role combination to hit first given his background, what types of companies or JD keywords to prioritise (e.g. startups with LangChain/RAG stacks, fintech with XGBoost/MLflow, analytics teams wanting Power BI + SQL)",
  "affirmation": "One powerful 12-18 word affirmation written specifically for Raju — references his name or his real skills"
}}"""

    elif email_type == "check":
        if applied >= GOAL:
            tone = "celebratory and proud — he crushed the goal"
        elif applied >= 15:
            tone = "encouraging and energetic — almost there, one last push will finish it"
        elif applied >= 5:
            tone = "urgent but not harsh — a strong afternoon sprint will save the day"
        else:
            tone = "firm, direct, caring — unless on Amazon shift (then understanding and supportive)"

        weakest_role = min(roles_data, key=lambda r: roles_data.get(r, 0))
        weakest_label = ROLES.get(weakest_role, weakest_role)

        instruction = f"""You are Raju's personal AI job hunt coach. Write a PROGRESS CHECK email.
Tone: {tone}
Current weakest role by count: {weakest_label} ({roles_data.get(weakest_role, 0)} applications)

Return ONLY valid JSON — no markdown fences, no extra text:
{{
  "headline": "headline reflecting exact progress {applied}/{GOAL} — honest, no emoji",
  "body": "4-5 sentences — acknowledge exact numbers for each role, reference today's schedule if relevant, be specific about what's been achieved and what gap remains, tone matches above",
  "action_plan": "2-3 sentences — concrete next-2-hours plan: specific role to focus on, specific type of company to target given his skills, realistic target number to hit before end of day",
  "role_insight": "1-2 sentences — point out which role is lagging ({weakest_label} at {roles_data.get(weakest_role, 0)}) and why it matters for his profile to have balanced coverage"
}}"""

    else:  # midnight
        if applied >= GOAL:
            tone = "celebratory, proud, set up for tomorrow"
        elif applied >= 15:
            tone = "positive but honest — good day, close to goal, tomorrow go further"
        elif applied >= 5:
            tone = "honest and constructive — below target, acknowledge why, clear tomorrow plan"
        else:
            tone = "honest, caring, no harsh judgement — reset and rebuild tomorrow (consider Amazon shift)"

        instruction = f"""You are Raju's personal AI job hunt coach. Write an END OF DAY SUMMARY email.
Tone: {tone}
Be honest about {applied}/{GOAL} — don't sugarcoat but don't crush either.

Return ONLY valid JSON — no markdown fences, no extra text:
{{
  "headline": "honest end-of-day headline for {applied}/{GOAL} — no emoji",
  "body": "4-5 sentences — reflect on today's full picture ({applied} total, role breakdown), acknowledge Amazon shift or weekend if context says so, celebrate wins even if small, be real about shortfall",
  "tomorrow_plan": "2-3 sentences — specific actionable plan for tomorrow: start time, which roles to hit first, a concrete number target per role to reach {GOAL} total",
  "strength": "1-2 sentences — one specific skill or project from his CV to highlight MORE in tomorrow's applications (e.g. his Agentic AI Video Synthesizer for AI roles, or KPMG Tableau dashboard for DA roles) and why recruiters will respond to it"
}}"""

    prompt = (
        "You are Raju's deeply personal AI job hunt coach with full knowledge of his background.\n\n"
        f"{profile}\n{progress}\n{instruction}"
    )

    try:
        client   = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model    = "gemini-2.0-flash",
            contents = prompt,
        )
        text  = response.text.strip()
        match = _re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        print(f"Gemini error: {e}")

    return None

# ─── Background file watcher ─────────────────────────────────────────────────

def watch_folder(interval=30):
    """Polls every `interval` seconds; scans instantly when new .docx is detected."""
    log_path = os.path.join(BASE, "watcher.log")

    def log(msg):
        line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
        with open(log_path, "a") as f:
            f.write(line + "\n")

    log(f"Watcher started — polling every {interval}s for new .docx files in {BASE}")

    # Build initial snapshot of all .docx files
    def get_snapshot():
        snap = {}
        for root, dirs, files in os.walk(BASE):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for fname in files:
                if fname.lower().endswith('.docx'):
                    fpath = os.path.join(root, fname)
                    snap[fpath] = os.path.getmtime(fpath)
        return snap

    known = get_snapshot()
    log(f"Snapshot: {len(known)} existing .docx files")

    while True:
        time.sleep(interval)
        try:
            current = get_snapshot()
            new_files = [p for p in current if p not in known]
            if new_files:
                log(f"Detected {len(new_files)} new file(s): {[os.path.basename(p) for p in new_files]}")
                results = scan_and_log()
                log(f"Scan complete — {len(results)} new applications logged")
            known = current
        except Exception as e:
            log(f"Error: {e}")

# ─── CLI ──────────────────────────────────────────────────────────────────────

def print_help():
    print("""
Job Application Tracker — Commands:
  python resume_tracker.py morning          Send 7 AM motivation email (unique each day)
  python resume_tracker.py midday           Send 12 PM progress check email
  python resume_tracker.py scan            Auto-classify all .docx files and log them
  python resume_tracker.py add <role> [n]  Log n applications (default 1)
                                            Roles: ai, da, ds, ml
  python resume_tracker.py check           Manual check + notification
  python resume_tracker.py summary         Show full history
  python resume_tracker.py setup           Configure email (run once)
  python resume_tracker.py schedule        Register 7 AM & 12 PM Windows scheduled tasks

Examples:
  python resume_tracker.py morning         (send today's motivation — different every day)
  python resume_tracker.py add ai 5        (log 5 AI Engineer applications)
  python resume_tracker.py add da 3        (log 3 Data Analyst applications)
  python resume_tracker.py midday          (see how many done by noon)
""")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "check":
        check_and_notify()
    elif args[0] == "morning":
        morning_motivate()
    elif args[0] == "midday":
        midday_check()
    elif args[0] == "midnight":
        midnight_summary()
    elif args[0] == "add":
        if len(args) < 2:
            print("Usage: python resume_tracker.py add <role> [n]")
            print("Roles:", ", ".join(ROLES.keys()))
        else:
            role = args[1].lower()
            n    = int(args[2]) if len(args) > 2 else 1
            if role not in ROLES:
                print(f"Unknown role '{role}'. Valid: {', '.join(ROLES.keys())}")
            else:
                entry = add_application(role, n)
                total = entry["total"]
                print(f"Logged {n}x {ROLES[role]}. Today: {total}/{GOAL}")
                auto_push_log()
                if total >= GOAL:
                    toast("GOAL ACHIEVED!", f"{total}/{GOAL} jobs applied today! YOU DID IT!")
                else:
                    toast(f"{total}/{GOAL} Jobs Applied", f"{GOAL - total} more to go today! Keep pushing!")
    elif args[0] == "scan":
        scan_and_log()
    elif args[0] == "watch":
        watch_folder()
    elif args[0] == "summary":
        show_summary()
    elif args[0] == "setup":
        setup_email()
    elif args[0] == "schedule":
        setup_scheduler()
    else:
        print_help()
