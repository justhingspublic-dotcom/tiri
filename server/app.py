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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html import escape
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
        # 垃圾桶（軟刪除）：deleted_at 非 NULL＝在垃圾桶，7 天後由 purge_trash 永久清除
        cols = [r[1] for r in db.execute("PRAGMA table_info(submissions)")]
        if "deleted_at" not in cols:
            db.execute("ALTER TABLE submissions ADD COLUMN deleted_at TEXT")


TRASH_KEEP_DAYS = 7


def purge_trash(db):
    """垃圾桶逾期清除：進垃圾桶超過 7 天的永久刪除（每次開後台列表時順手清）"""
    cutoff = (datetime.now(TAIPEI) - timedelta(days=TRASH_KEEP_DAYS)).strftime("%Y-%m-%d %H:%M:%S")
    db.execute("DELETE FROM submissions WHERE deleted_at IS NOT NULL AND deleted_at < ?", (cutoff,))
    db.commit()


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

def send_mail(subject, body, html=None, force_real=False):
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

    if html:  # multipart/alternative：純文字給不吃 HTML 的客戶端當備援
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(body, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))
    else:
        msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = get_setting("MAIL_FROM") or user
    msg["To"] = ", ".join(to_addrs)

    with smtplib.SMTP(host, int(get_setting("SMTP_PORT", "587")), timeout=15) as s:
        s.starttls()
        s.login(user, get_setting("SMTP_PASS", ""))
        s.sendmail(msg["From"], to_addrs, msg.as_string())
    return "sent"


def notification_html(form_name, fields, page_url, when, intro):
    """通知信 HTML 版：填寫內容以表格呈現（樣式全內聯，遷就信件客戶端）"""
    def esc(s):
        return escape(str(s), quote=True)

    td = "border:1px solid #e3e6ea;padding:9px 12px;vertical-align:top;"
    rows = "".join(
        f'<tr><td style="{td}width:132px;background:#f6f7f9;color:#57606a;'
        f'font-weight:600;white-space:nowrap;">{esc(f.get("label", ""))}</td>'
        f'<td style="{td}color:#1f2328;">{esc(f.get("value", "")).replace(chr(10), "<br>") or "—"}</td></tr>'
        for f in fields if isinstance(f, dict) and f.get("label")
    )
    intro_html = (
        f'<p style="margin:0 0 16px;font-size:14px;line-height:1.7;color:#1f2328;">'
        f'{esc(intro).replace(chr(10), "<br>")}</p>' if intro else ""
    )
    return (
        '<div style="font-family:-apple-system,\'PingFang TC\',\'Noto Sans TC\','
        "'Microsoft JhengHei',sans-serif;max-width:640px;\">"
        f"{intro_html}"
        f'<h2 style="margin:0 0 4px;font-size:16px;color:#7e3268;">{esc(form_name)}</h2>'
        f'<p style="margin:0 0 14px;font-size:12.5px;line-height:1.7;color:#6b7280;">'
        f'{esc(when)}<br><a href="{esc(page_url)}" style="color:#6b7280;">{esc(page_url)}</a></p>'
        f'<table cellpadding="0" cellspacing="0" '
        f'style="border-collapse:collapse;width:100%;font-size:14px;line-height:1.6;">{rows}</table>'
        '<p style="margin:16px 0 0;font-size:12px;color:#9aa1a9;">'
        "此信由 TIRI 網站表單系統自動寄出</p></div>"
    )


def send_notification(form_name, fields, page_url, when, base_slug=""):
    # 每表單可自訂主旨與開頭文字（設定頁「通知信文案」），留空用預設
    subject = get_setting(f"MAIL_SUBJ_{base_slug}", "") or f"[TIRI 網站] {form_name} — 新的表單填寫"
    intro = get_setting(f"MAIL_INTRO_{base_slug}", "") or ""

    lines = []  # 純文字版：給不顯示 HTML 的客戶端當備援
    if intro:
        lines += [intro, ""]
    lines += [f"表單：{form_name}", f"時間:{when}", f"頁面:{page_url}", ""]
    for f in fields:
        lines.append(f"{f.get('label', '')}:{f.get('value', '')}")
    html = notification_html(form_name, fields, page_url, when, intro)
    return send_mail(subject, "\n".join(lines), html=html)


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
        # 前端 fetch 送出時帶 Accept: application/json → 回 JSON 給按鈕填色動畫用；
        # 無 JS 時維持傳統 redirect + flash fallback
        wants_json = "application/json" in (request.headers.get("Accept") or "")
        # 密碼可在後台「帳號設定」變更（存 settings 表，蓋過 .env 預設）
        if email == ADMIN_EMAIL.lower() and password == get_setting("ADMIN_PASS", ADMIN_PASSWORD):
            session["admin"] = email
            flash("登入成功", "success")   # 跳轉後由 base.html 的右下角 toast 顯示
            if wants_json:
                return jsonify(ok=True, redirect="/admin")
            return redirect("/admin")
        if wants_json:
            return jsonify(ok=False, error="帳號或密碼錯誤"), 401
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
    # 收件匣右端顯示總數（不含垃圾桶）
    try:
        inbox_n = get_db().execute(
            "SELECT COUNT(*) FROM submissions WHERE deleted_at IS NULL"
        ).fetchone()[0]
    except Exception:
        inbox_n = None
    return [
        {"key": "dashboard", "title": "儀表板", "url": "/admin", "icon": "gauge"},
        {"key": "inbox", "title": "收件匣", "url": "/admin/inbox", "icon": "inbox", "count": inbox_n},
        {"key": "trash", "title": "垃圾桶", "url": "/admin/trash", "icon": "trash-2"},
        {"title": "設定", "icon": "settings", "sub": [
            {"key": "settings", "title": "郵件設定", "url": "/admin/settings"},
            {"key": "account", "title": "帳號設定", "url": "/admin/account"},
        ]},
    ]


def query_rows(slug, deleted=False):
    """deleted=False＝收件匣（未刪），True＝垃圾桶"""
    db = get_db()
    cond = "deleted_at IS NOT NULL" if deleted else "deleted_at IS NULL"
    order = "deleted_at DESC" if deleted else "id DESC"
    if slug:
        return db.execute(
            f"SELECT * FROM submissions WHERE {cond} AND form_slug LIKE ? ORDER BY {order} LIMIT 500",
            (slug + "%",),
        ).fetchall()
    return db.execute(f"SELECT * FROM submissions WHERE {cond} ORDER BY {order} LIMIT 500").fetchall()


def row_dict(r):
    fields = [f for f in json.loads(r["fields_json"]) if isinstance(f, dict)]
    # Gmail 式列表：第一個有值的欄位當「寄件人」（通常是姓名/公司名稱），其餘進摘要
    idx = next((i for i, f in enumerate(fields) if str(f.get("value", "")).strip()), None)
    d = {
        "id": r["id"],
        "submitted_at": r["submitted_at"],
        "form_name": r["form_name"],
        "form_slug": r["form_slug"],
        "mail_status": (r["mail_status"] or "").split(":")[0].strip(),
        "fields": fields,
        "display_name": fields[idx]["value"] if idx is not None else "（未填）",
        "snippet": [f for i, f in enumerate(fields)
                    if i != idx and str(f.get("value", "")).strip()],
    }
    if r["deleted_at"]:  # 垃圾桶列：算剩幾天永久刪除（至少顯示 1 天）
        deleted = datetime.strptime(r["deleted_at"], "%Y-%m-%d %H:%M:%S")
        expire = deleted + timedelta(days=TRASH_KEEP_DAYS)
        d["deleted_at"] = r["deleted_at"]
        d["days_left"] = max(1, (expire.date() - datetime.now(TAIPEI).date()).days)
    return d


@app.route("/admin")
@require_auth
def dashboard():
    db = get_db()
    purge_trash(db)
    now = datetime.now(TAIPEI)
    # 所有統計都不含垃圾桶（deleted_at IS NULL）
    total = db.execute("SELECT COUNT(*) FROM submissions WHERE deleted_at IS NULL").fetchone()[0]
    today_n = db.execute(
        "SELECT COUNT(*) FROM submissions WHERE deleted_at IS NULL AND submitted_at LIKE ?",
        (now.strftime("%Y-%m-%d") + "%",),
    ).fetchone()[0]
    week_n = db.execute(
        "SELECT COUNT(*) FROM submissions WHERE deleted_at IS NULL AND submitted_at >= ?",
        ((now - timedelta(days=7)).strftime("%Y-%m-%d"),),
    ).fetchone()[0]
    fail_n = db.execute(
        "SELECT COUNT(*) FROM submissions WHERE deleted_at IS NULL AND mail_status LIKE 'error%'"
    ).fetchone()[0]

    counts = dict(
        db.execute("SELECT form_slug, COUNT(*) FROM submissions WHERE deleted_at IS NULL GROUP BY form_slug").fetchall()
    )
    form_stats = []
    for s, n in FORM_NAMES.items():
        c = sum(v for k, v in counts.items() if k.startswith(s))
        form_stats.append({
            "slug": s, "name": n, "icon": NAV_ICONS[s], "count": c,
            "pct": round(c * 100 / total) if total else 0,
        })

    recent = [row_dict(r) for r in db.execute(
        "SELECT * FROM submissions WHERE deleted_at IS NULL ORDER BY id DESC LIMIT 8"
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
    db = get_db()
    purge_trash(db)
    slug = request.args.get("form", "")
    # 一次載入全部（每列帶 data-slug），篩選在前端做：segment 滑塊才有滑動切換、不用整頁重載
    rows = [row_dict(r) for r in query_rows("")]
    counts = dict(
        db.execute("SELECT form_slug, COUNT(*) FROM submissions WHERE deleted_at IS NULL GROUP BY form_slug").fetchall()
    )
    filters = [{"slug": "", "name": "全部", "count": sum(counts.values())}]
    for s, n in FORM_NAMES.items():
        filters.append({"slug": s, "name": n,
                        "count": sum(v for k, v in counts.items() if k.startswith(s))})
    return render_template(
        "inbox.html",
        nav_items=nav_items(),
        active="inbox",
        mode="inbox",
        slug=slug,
        page_name=FORM_NAMES.get(slug, ""),
        filters=filters,
        rows=rows,
    )


@app.route("/admin/trash")
@require_auth
def trash():
    db = get_db()
    purge_trash(db)
    # 垃圾桶不做 segment（使用者裁決）：表單類型改放篩選面板，filters 只給面板下拉用
    rows = [row_dict(r) for r in query_rows("", deleted=True)]
    filters = [{"slug": s, "name": n} for s, n in FORM_NAMES.items()]
    return render_template(
        "inbox.html",
        nav_items=nav_items(),
        active="trash",
        mode="trash",
        slug="",
        page_name="",
        filters=filters,
        rows=rows,
    )


def _post_ids():
    data = request.get_json(silent=True) or {}
    return [int(i) for i in data.get("ids", []) if str(i).isdigit()]


@app.route("/admin/inbox/delete", methods=["POST"])
@require_auth
def inbox_delete():
    # 軟刪除＝移至垃圾桶（deleted_at 蓋時間戳），7 天內可還原
    ids = _post_ids()
    if not ids:
        return jsonify(ok=False, message="沒有選取任何資料"), 400
    db = get_db()
    now = datetime.now(TAIPEI).strftime("%Y-%m-%d %H:%M:%S")
    cur = db.execute(
        f"UPDATE submissions SET deleted_at = ? WHERE deleted_at IS NULL AND id IN ({','.join('?' * len(ids))})",
        [now] + ids,
    )
    db.commit()
    return jsonify(ok=True, deleted=cur.rowcount, message=f"已將 {cur.rowcount} 筆收件移至垃圾桶")


@app.route("/admin/trash/restore", methods=["POST"])
@require_auth
def trash_restore():
    ids = _post_ids()
    if not ids:
        return jsonify(ok=False, message="沒有選取任何資料"), 400
    db = get_db()
    cur = db.execute(
        f"UPDATE submissions SET deleted_at = NULL WHERE deleted_at IS NOT NULL AND id IN ({','.join('?' * len(ids))})",
        ids,
    )
    db.commit()
    return jsonify(ok=True, restored=cur.rowcount, message=f"已還原 {cur.rowcount} 筆收件")


@app.route("/admin/trash/delete", methods=["POST"])
@require_auth
def trash_delete():
    ids = _post_ids()
    if not ids:
        return jsonify(ok=False, message="沒有選取任何資料"), 400
    db = get_db()
    cur = db.execute(
        f"DELETE FROM submissions WHERE deleted_at IS NOT NULL AND id IN ({','.join('?' * len(ids))})",
        ids,
    )
    db.commit()
    return jsonify(ok=True, deleted=cur.rowcount, message=f"已永久刪除 {cur.rowcount} 筆收件")


SETTING_FIELDS = [
    ("MAIL_TO", "通知信收件人", "有人填表單時要通知誰。多個信箱用逗號分隔，例：judy@tiri.tw, office@tiri.tw"),
    ("MAIL_FROM", "寄件人顯示信箱", "留空＝用 SMTP 帳號"),
    ("SMTP_HOST", "SMTP 主機", "Gmail 是 smtp.gmail.com"),
    ("SMTP_PORT", "SMTP 埠號", "通常是 587"),
    ("SMTP_USER", "SMTP 帳號", "寄信用的信箱帳號"),
]


def is_fetch():
    """前端 fetch 儲存（不重整頁面）帶這個標頭；回 JSON 而非 redirect"""
    return request.headers.get("X-Requested-With") == "fetch"


def save_settings_section(section):
    """各卡片獨立儲存：只動自己那一區的鍵，避免互相洗掉"""
    f = request.form
    if section == "smtp":
        for key in ("MAIL_FROM", "SMTP_HOST", "SMTP_PORT", "SMTP_USER"):
            set_setting(key, f.get(key, "").strip())
        if f.get("SMTP_PASS", "").strip():  # 密碼留空＝不變更
            # Google 應用程式密碼顯示為「xxxx xxxx xxxx xxxx」帶空格，SMTP 登入要去掉
            set_setting("SMTP_PASS", f.get("SMTP_PASS").replace(" ", "").strip())
    elif section == "notify":  # 寄測試信用：一次套用通知卡整卡內容
        set_setting("MAIL_TO", f.get("MAIL_TO", "").strip())
        set_setting("MAIL_DRY_RUN", "1" if f.get("MAIL_DRY_RUN") else "0")
    elif section == "mailto":  # 收件人輸入框內嵌儲存鈕：只存收件人
        set_setting("MAIL_TO", f.get("MAIL_TO", "").strip())
    elif section == "dry":     # 測試模式勾勾：勾/取消即時套用
        set_setting("MAIL_DRY_RUN", "1" if f.get("MAIL_DRY_RUN") else "0")
    elif section == "copy":
        # 各表單通知信文案（主旨＋開頭文字；留空＝用預設）
        for slug in FORM_NAMES:
            set_setting(f"MAIL_SUBJ_{slug}", f.get(f"MAIL_SUBJ_{slug}", "").strip())
            set_setting(f"MAIL_INTRO_{slug}", f.get(f"MAIL_INTRO_{slug}", "").strip())


@app.route("/admin/settings", methods=["GET", "POST"])
@require_auth
def settings():
    if request.method == "POST":
        section = request.form.get("section", "")
        if section in ("smtp", "notify", "copy", "mailto", "dry"):
            save_settings_section(section)
        else:  # 沒帶 section 的舊式整頁提交：全存
            for s in ("smtp", "notify", "copy"):
                save_settings_section(s)
        if is_fetch():
            return jsonify(ok=True, message="設定已儲存",
                           pw_set=bool(get_setting("SMTP_PASS")))
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
    # 先存兩張寄信相關卡片目前的內容，讓「填完直接按測試」也能生效
    save_settings_section("smtp")
    save_settings_section("notify")
    when = datetime.now(TAIPEI).strftime("%Y-%m-%d %H:%M:%S")
    body = (f"這是一封測試信（{when}）。\n\n"
            "收到這封信代表 TIRI 網站表單的通知功能設定成功，"
            "之後有人填寫報名表單時，通知就會寄到這個信箱。")
    try:
        status = send_mail("[TIRI 網站] 通知信測試", body, force_real=True)
    except Exception as e:
        app.logger.exception("測試信寄送失敗")
        status = f"{e}"
    ok = status == "sent"
    message = ("測試信已寄出！請到收件信箱確認（沒看到的話檢查垃圾信件匣）" if ok
               else f"寄送失敗：{str(status).replace('error: ', '')}")
    if is_fetch():
        return jsonify(ok=ok, message=message, pw_set=bool(get_setting("SMTP_PASS")))
    flash(message, "success" if ok else "danger")
    return redirect("/admin/settings")


@app.route("/admin/account", methods=["GET", "POST"])
@require_auth
def account():
    if request.method == "POST":
        section = request.form.get("section", "")

        if section == "password":
            pw = request.form.get("new_password", "")
            pw2 = request.form.get("new_password2", "")
            if not pw or pw != pw2:
                msg, ok = "兩次輸入的新密碼不一致，密碼未變更", False
            elif len(pw) < 8:
                msg, ok = "新密碼至少 8 個字元，密碼未變更", False
            else:
                set_setting("ADMIN_PASS", pw)
                msg, ok = "密碼已更新，下次登入請用新密碼", True
        else:  # profile：只存基本資料，與密碼互不相干
            set_setting("ADMIN_NICKNAME", request.form.get("nickname", "").strip())
            msg, ok = "基本資料已儲存", True

        if is_fetch():
            return jsonify(ok=ok, message=msg,
                           nickname=get_setting("ADMIN_NICKNAME", "秘書處") or "秘書處")
        flash(msg, "success" if ok else "danger")
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


@app.route("/")
def index():
    # 這台伺服器只有收件 API 與後台，根目錄一律導向後台（未登入會再轉登入頁）
    return redirect("/admin")


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
