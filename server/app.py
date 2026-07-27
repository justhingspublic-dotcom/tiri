# TIRI 過渡期表單收件後端
# 收前台表單 POST -> 存 SQLite -> 寄 email 通知
# 後台 UI 依 backend-design uikit（typeui Dashboard）規範
# 執行: python app.py  (預設 http://0.0.0.0:8000)

import json
import os
import smtplib
import sqlite3
from datetime import datetime, timezone, timedelta
from email.header import Header
from email.mime.text import MIMEText
from functools import wraps
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv
from flask import (Flask, Response, flash, g, jsonify, redirect,
                   render_template, request, send_file, session)

load_dotenv(Path(__file__).parent / ".env")

DB_PATH = Path(__file__).parent / "submissions.db"
TAIPEI = timezone(timedelta(hours=8))

FORM_NAMES = {
    "join": "加入會員",
    "trainbod": "董監事課程",
    "tiric": "TIRIC 課程",
    "bodperform": "董事會績效評估",
    "corpperform": "公司治理評估",
    "contact": "聯絡我們",
}

NAV_ICONS = {
    "join": "user-round-plus",
    "trainbod": "graduation-cap",
    "tiric": "book-open",
    "bodperform": "clipboard-check",
    "corpperform": "shield-check",
    "contact": "mail",
}

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "office@tiri.tw")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "tiri1234")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "tiri-transitional-backend")


# ---------- DB ----------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                form_slug TEXT NOT NULL,
                form_name TEXT,
                page_url TEXT,
                fields_json TEXT NOT NULL,
                ip TEXT,
                submitted_at TEXT NOT NULL,
                mail_status TEXT
            )"""
        )
        db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")


def get_setting(key, default=None):
    """後台設定優先，其次 .env，最後預設值"""
    row = get_db().execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if row is not None and row[0] != "":
        return row[0]
    return os.environ.get(key, default)


def set_setting(key, value):
    db = get_db()
    db.execute(
        "INSERT INTO settings (key, value) VALUES (?, ?)"
        " ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (key, value),
    )
    db.commit()


# ---------- CORS ----------

def allowed_origin(origin):
    allow = os.environ.get("ALLOWED_ORIGINS", "*")
    if allow.strip() == "*":
        return "*"
    origins = [o.strip() for o in allow.split(",") if o.strip()]
    return origin if origin in origins else None


@app.after_request
def add_cors(resp):
    origin = allowed_origin(request.headers.get("Origin", ""))
    if origin:
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    # 過渡期後台：禁止快取（Safari 快取造成「改了看不到」多次誤判，規模小、no-store 成本可忽略）
    resp.headers["Cache-Control"] = "no-store"
    return resp


# ---------- Mail ----------

def send_mail(subject, body, force_real=False):
    """回傳狀態字串；force_real=True 時忽略測試模式真的寄（給「寄測試信」用）"""
    to_raw = get_setting("MAIL_TO", "")
    to_addrs = [a.strip() for a in to_raw.split(",") if a.strip()]

    if not force_real and get_setting("MAIL_DRY_RUN", "0") == "1":
        app.logger.warning("MAIL_DRY_RUN=1，僅顯示不寄出（收件人:%s）:\n%s\n%s", to_raw, subject, body)
        return "dry-run"

    host = get_setting("SMTP_HOST")
    user = get_setting("SMTP_USER")
    if not host or not user:
        return "error: 尚未設定 SMTP 主機/帳號"
    if not to_addrs:
        return "error: 尚未設定通知信收件人"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = get_setting("MAIL_FROM") or user
    msg["To"] = ", ".join(to_addrs)

    with smtplib.SMTP(host, int(get_setting("SMTP_PORT", "587")), timeout=15) as s:
        s.starttls()
        s.login(user, get_setting("SMTP_PASS", ""))
        s.sendmail(msg["From"], to_addrs, msg.as_string())
    return "sent"


def send_notification(form_name, fields, page_url, when, base_slug=""):
    # 每表單可自訂主旨與開頭文字（設定頁「通知信文案」），留空用預設
    subject = get_setting(f"MAIL_SUBJ_{base_slug}", "") or f"[TIRI 網站] {form_name} — 新的表單填寫"
    intro = get_setting(f"MAIL_INTRO_{base_slug}", "") or ""

    lines = []
    if intro:
        lines += [intro, ""]
    lines += [f"表單：{form_name}", f"時間:{when}", f"頁面:{page_url}", ""]
    for f in fields:
        lines.append(f"{f.get('label', '')}:{f.get('value', '')}")
    return send_mail(subject, "\n".join(lines))


# ---------- 表單收件 API ----------

@app.route("/api/submit/<slug>", methods=["POST", "OPTIONS"])
def submit(slug):
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json(silent=True) or {}
    fields = data.get("fields", [])

    # honeypot：前端藏一個真人不會填的欄位
    if data.get("website"):
        return jsonify(ok=True)

    if not isinstance(fields, list) or not any(
        str(f.get("value", "")).strip() for f in fields if isinstance(f, dict)
    ):
        return jsonify(ok=False, error="empty form"), 400

    base_slug = slug.split("-")[0]
    form_name = FORM_NAMES.get(base_slug, slug)
    when = datetime.now(TAIPEI).strftime("%Y-%m-%d %H:%M:%S")
    page_url = str(data.get("page", ""))[:500]

    try:
        mail_status = send_notification(form_name, fields, page_url, when, base_slug)
    except Exception as e:  # 寄信失敗仍要保住資料
        app.logger.exception("寄信失敗")
        mail_status = f"error: {e}"

    db = get_db()
    db.execute(
        "INSERT INTO submissions (form_slug, form_name, page_url, fields_json, ip, submitted_at, mail_status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (slug, form_name, page_url, json.dumps(fields, ensure_ascii=False),
         request.headers.get("X-Forwarded-For", request.remote_addr), when, mail_status),
    )
    db.commit()
    return jsonify(ok=True)


# ---------- 後台：登入 ----------

def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/admin/login")
        return fn(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_account():
    try:
        nickname = get_setting("ADMIN_NICKNAME", "秘書處") or "秘書處"
    except Exception:
        nickname = "秘書處"
    return {"nickname": nickname, "admin_email": ADMIN_EMAIL}


@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        # 密碼可在後台「帳號設定」變更（存 settings 表，蓋過 .env 預設）
        if email == ADMIN_EMAIL.lower() and password == get_setting("ADMIN_PASS", ADMIN_PASSWORD):
            session["admin"] = email
            return redirect("/admin")
        flash("帳號或密碼錯誤", "danger")
        return redirect("/admin/login")
    if session.get("admin"):
        return redirect("/admin")
    return render_template("login.html")


@app.route("/admin/logout", methods=["POST"])
def logout():
    session.pop("admin", None)
    return redirect("/admin/login")


# ---------- 後台：頁面 ----------

def nav_items():
    return [
        {"key": "dashboard", "title": "儀表板", "url": "/admin", "icon": "gauge"},
        {"key": "inbox", "title": "收件匣", "url": "/admin/inbox", "icon": "inbox"},
        {"title": "設定", "icon": "settings", "sub": [
            {"key": "settings", "title": "郵件設定", "url": "/admin/settings"},
            {"key": "account", "title": "帳號設定", "url": "/admin/account"},
        ]},
    ]


def query_rows(slug):
    db = get_db()
    if slug:
        return db.execute(
            "SELECT * FROM submissions WHERE form_slug LIKE ? ORDER BY id DESC LIMIT 500",
            (slug + "%",),
        ).fetchall()
    return db.execute("SELECT * FROM submissions ORDER BY id DESC LIMIT 500").fetchall()


def row_dict(r):
    return {
        "id": r["id"],
        "submitted_at": r["submitted_at"],
        "form_name": r["form_name"],
        "form_slug": r["form_slug"],
        "mail_status": (r["mail_status"] or "").split(":")[0].strip(),
        "fields": json.loads(r["fields_json"]),
    }


@app.route("/admin")
@require_auth
def dashboard():
    db = get_db()
    now = datetime.now(TAIPEI)
    total = db.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
    today_n = db.execute(
        "SELECT COUNT(*) FROM submissions WHERE submitted_at LIKE ?",
        (now.strftime("%Y-%m-%d") + "%",),
    ).fetchone()[0]
    week_n = db.execute(
        "SELECT COUNT(*) FROM submissions WHERE submitted_at >= ?",
        ((now - timedelta(days=7)).strftime("%Y-%m-%d"),),
    ).fetchone()[0]
    fail_n = db.execute(
        "SELECT COUNT(*) FROM submissions WHERE mail_status LIKE 'error%'"
    ).fetchone()[0]

    counts = dict(
        db.execute("SELECT form_slug, COUNT(*) FROM submissions GROUP BY form_slug").fetchall()
    )
    form_stats = []
    for s, n in FORM_NAMES.items():
        c = sum(v for k, v in counts.items() if k.startswith(s))
        form_stats.append({
            "slug": s, "name": n, "icon": NAV_ICONS[s], "count": c,
            "pct": round(c * 100 / total) if total else 0,
        })

    recent = [row_dict(r) for r in db.execute(
        "SELECT * FROM submissions ORDER BY id DESC LIMIT 8"
    ).fetchall()]

    return render_template(
        "dashboard.html",
        nav_items=nav_items(),
        active="dashboard",
        total=total, today_n=today_n, week_n=week_n, fail_n=fail_n,
        form_stats=form_stats,
        recent=recent,
        dry=get_setting("MAIL_DRY_RUN", "0") == "1",
        mail_to=get_setting("MAIL_TO", "") or "",
    )


@app.route("/admin/inbox")
@require_auth
def inbox():
    slug = request.args.get("form", "")
    # 一次載入全部（每列帶 data-slug），篩選在前端做：segment 滑塊才有滑動切換、不用整頁重載
    rows = [row_dict(r) for r in query_rows("")]
    counts = dict(
        get_db().execute("SELECT form_slug, COUNT(*) FROM submissions GROUP BY form_slug").fetchall()
    )
    filters = [{"slug": "", "name": "全部", "count": sum(counts.values())}]
    for s, n in FORM_NAMES.items():
        filters.append({"slug": s, "name": n,
                        "count": sum(v for k, v in counts.items() if k.startswith(s))})
    return render_template(
        "inbox.html",
        nav_items=nav_items(),
        active="inbox",
        slug=slug,
        page_name=FORM_NAMES.get(slug, ""),
        filters=filters,
        rows=rows,
    )


SETTING_FIELDS = [
    ("MAIL_TO", "通知信收件人", "有人填表單時要通知誰。多個信箱用逗號分隔，例：judy@tiri.tw, office@tiri.tw"),
    ("MAIL_FROM", "寄件人顯示信箱", "留空＝用 SMTP 帳號"),
    ("SMTP_HOST", "SMTP 主機", "Gmail 是 smtp.gmail.com"),
    ("SMTP_PORT", "SMTP 埠號", "通常是 587"),
    ("SMTP_USER", "SMTP 帳號", "寄信用的信箱帳號"),
]


def save_settings_from_form():
    for key, _, _ in SETTING_FIELDS:
        set_setting(key, request.form.get(key, "").strip())
    if request.form.get("SMTP_PASS", "").strip():  # 密碼留空＝不變更
        # Google 應用程式密碼顯示為「xxxx xxxx xxxx xxxx」帶空格，SMTP 登入要去掉
        set_setting("SMTP_PASS", request.form.get("SMTP_PASS").replace(" ", "").strip())
    set_setting("MAIL_DRY_RUN", "1" if request.form.get("MAIL_DRY_RUN") else "0")
    # 各表單通知信文案（主旨＋開頭文字；留空＝用預設）
    for slug in FORM_NAMES:
        set_setting(f"MAIL_SUBJ_{slug}", request.form.get(f"MAIL_SUBJ_{slug}", "").strip())
        set_setting(f"MAIL_INTRO_{slug}", request.form.get(f"MAIL_INTRO_{slug}", "").strip())


@app.route("/admin/settings", methods=["GET", "POST"])
@require_auth
def settings():
    if request.method == "POST":
        save_settings_from_form()
        flash("設定已儲存", "success")
        return redirect("/admin/settings")

    values = {key: get_setting(key, "") or "" for key, _, _ in SETTING_FIELDS}
    pw_set = bool(get_setting("SMTP_PASS"))
    pw_hint = "已設定，留空＝維持不變" if pw_set else "尚未設定。Gmail 請用「應用程式密碼」"
    mail_copy = [
        {
            "slug": s, "name": n,
            "subj": get_setting(f"MAIL_SUBJ_{s}", "") or "",
            "intro": get_setting(f"MAIL_INTRO_{s}", "") or "",
            "default_subj": f"[TIRI 網站] {n} — 新的表單填寫",
        }
        for s, n in FORM_NAMES.items()
    ]
    return render_template(
        "settings.html",
        nav_items=nav_items(),
        active="settings",
        fields=SETTING_FIELDS,
        values=values,
        pw_set=pw_set,
        pw_hint=pw_hint,
        mail_copy=mail_copy,
        dry=get_setting("MAIL_DRY_RUN", "0") == "1",
    )


@app.route("/admin/settings/test", methods=["POST"])
@require_auth
def settings_test():
    save_settings_from_form()  # 先存目前表單內容，讓「填完直接按測試」也能生效
    when = datetime.now(TAIPEI).strftime("%Y-%m-%d %H:%M:%S")
    body = (f"這是一封測試信（{when}）。\n\n"
            "收到這封信代表 TIRI 網站表單的通知功能設定成功，"
            "之後有人填寫報名表單時，通知就會寄到這個信箱。")
    try:
        status = send_mail("[TIRI 網站] 通知信測試", body, force_real=True)
    except Exception as e:
        app.logger.exception("測試信寄送失敗")
        status = f"{e}"
    if status == "sent":
        flash("測試信已寄出！請到收件信箱確認（沒看到的話檢查垃圾信件匣）", "success")
    else:
        flash(f"寄送失敗：{status.replace('error: ', '')}", "danger")
    return redirect("/admin/settings")


@app.route("/admin/account", methods=["GET", "POST"])
@require_auth
def account():
    if request.method == "POST":
        set_setting("ADMIN_NICKNAME", request.form.get("nickname", "").strip())
        pw = request.form.get("new_password", "")
        pw2 = request.form.get("new_password2", "")
        if pw or pw2:
            if pw != pw2:
                flash("兩次輸入的新密碼不一致，密碼未變更", "danger")
                return redirect("/admin/account")
            if len(pw) < 8:
                flash("新密碼至少 8 個字元，密碼未變更", "danger")
                return redirect("/admin/account")
            set_setting("ADMIN_PASS", pw)
            flash("暱稱與密碼已更新", "success")
        else:
            flash("帳號設定已儲存", "success")
        return redirect("/admin/account")

    return render_template("account.html", nav_items=nav_items(), active="account")


@app.route("/admin/export.csv")
@require_auth
def export_csv():
    import csv
    import io

    slug = request.args.get("form", "")
    rows = query_rows(slug)

    labels = []
    for r in rows:  # 欄位名依出現順序聯集（不同表單欄位不同）
        for f in json.loads(r["fields_json"]):
            if f.get("label") and f["label"] not in labels:
                labels.append(f["label"])

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["編號", "時間", "表單"] + labels + ["通知信"])
    for r in rows:
        values = {f.get("label"): f.get("value", "") for f in json.loads(r["fields_json"])}
        w.writerow([r["id"], r["submitted_at"], r["form_name"]]
                   + [values.get(l, "") for l in labels] + [r["mail_status"]])

    name = (slug or "all") + "-submissions.csv"
    return Response(
        chr(0xFEFF) + buf.getvalue(),  # BOM 讓 Excel 正確認 UTF-8
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={name}"},
    )


@app.route("/favicon.ico")
def favicon():
    # 與前台同一顆 favicon，檔案放在 server/ 內，後端單獨部署也帶著走
    return send_file(Path(__file__).parent / "favicon.ico", mimetype="image/x-icon")


@app.route("/healthz")
def healthz():
    return "ok"


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
