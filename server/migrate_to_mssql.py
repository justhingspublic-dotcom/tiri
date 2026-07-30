# 一次性遷移：把舊 settings key-value 表拆成 mail_settings（一列式）＋ mail_copy（一表單一筆 JSON）
# 來源優先序：該庫既有 settings 表 → 本機 SQLite submissions.db → .env
# 連線資訊讀 .env；跑多次安全（已存在的不覆蓋）；完成後 DROP 舊 settings 表
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pymssql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")
SERVER = os.environ["DB_SERVER"]
USER = os.environ["DB_USER"]
PASS = os.environ["DB_PASS"]
NOW = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M:%S")

FORM_NAMES = {
    "join": "加入會員", "trainbod": "董監事課程", "tiric": "TIRIC 課程",
    "bodperform": "董事會績效評估", "corpperform": "公司治理評估", "contact": "聯絡我們",
}

DDL = [
    """IF OBJECT_ID('submissions','U') IS NULL
       CREATE TABLE submissions (
           id INT IDENTITY(1,1) PRIMARY KEY,
           form_slug NVARCHAR(100) NOT NULL, form_name NVARCHAR(200) NULL,
           page_url NVARCHAR(500) NULL, fields_json NVARCHAR(MAX) NOT NULL,
           ip NVARCHAR(100) NULL, submitted_at NVARCHAR(19) NOT NULL,
           mail_status NVARCHAR(500) NULL, deleted_at NVARCHAR(19) NULL)""",
    """IF OBJECT_ID('mail_settings','U') IS NULL
       CREATE TABLE mail_settings (
           id INT PRIMARY KEY,
           smtp_host NVARCHAR(200) NULL, smtp_port NVARCHAR(10) NULL,
           smtp_user NVARCHAR(255) NULL, smtp_pass NVARCHAR(255) NULL,
           mail_to NVARCHAR(500) NULL,
           dry_run BIT NOT NULL DEFAULT 0, updated_at NVARCHAR(19) NULL)""",
    """IF OBJECT_ID('mail_copy','U') IS NULL
       CREATE TABLE mail_copy (
           form_slug NVARCHAR(50) PRIMARY KEY, form_name NVARCHAR(100) NULL,
           copy_json NVARCHAR(MAX) NULL, updated_at NVARCHAR(19) NULL)""",
    """IF OBJECT_ID('users','U') IS NULL
       CREATE TABLE users (
           id INT IDENTITY(1,1) PRIMARY KEY, email NVARCHAR(255) NOT NULL UNIQUE,
           password_hash NVARCHAR(500) NOT NULL, nickname NVARCHAR(100) NULL,
           created_at NVARCHAR(19) NULL)""",
]


def load_kv(cur):
    """舊 settings 表（該庫有就用它，否則退本機 SQLite）"""
    cur.execute("SELECT CASE WHEN OBJECT_ID('settings','U') IS NULL THEN 0 ELSE 1 END")
    if cur.fetchone()[0]:
        cur.execute("SELECT [key], [value] FROM settings")
        return dict(cur.fetchall())
    local = HERE / "submissions.db"
    if local.exists():
        return dict(sqlite3.connect(local).execute("SELECT key, value FROM settings"))
    return {}


def main():
    conn = pymssql.connect(server=SERVER, user=USER, password=PASS, autocommit=True)
    conn.cursor().execute("IF DB_ID('TIRI_dev') IS NULL CREATE DATABASE TIRI_dev")
    conn.close()

    for dbname in ("TIRI_dev", "TIRI"):
        c = pymssql.connect(server=SERVER, user=USER, password=PASS,
                            database=dbname, charset="UTF-8")
        x = c.cursor()
        kv = load_kv(x)
        for ddl in DDL:
            x.execute(ddl)

        # mail_settings：一列式（id=1），值從舊 kv 搬
        x.execute("SELECT COUNT(*) FROM mail_settings")
        if x.fetchone()[0] == 0:
            x.execute(
                "INSERT INTO mail_settings (id, smtp_host, smtp_port, smtp_user, smtp_pass,"
                " mail_to, dry_run, updated_at) VALUES (1,%s,%s,%s,%s,%s,%s,%s)",
                (kv.get("SMTP_HOST", ""), kv.get("SMTP_PORT", ""), kv.get("SMTP_USER", ""),
                 kv.get("SMTP_PASS", ""), kv.get("MAIL_TO", ""),
                 1 if kv.get("MAIL_DRY_RUN") == "1" else 0, NOW),
            )

        # mail_copy：一表單一筆，subject/intro 收進 copy_json
        for slug, name in FORM_NAMES.items():
            subj = (kv.get(f"MAIL_SUBJ_{slug}") or "").strip()
            intro = (kv.get(f"MAIL_INTRO_{slug}") or "").strip()
            payload = (json.dumps({"subject": subj, "intro": intro}, ensure_ascii=False)
                       if (subj or intro) else None)
            x.execute("IF NOT EXISTS (SELECT 1 FROM mail_copy WHERE form_slug = %s)"
                      " INSERT INTO mail_copy (form_slug, form_name, copy_json, updated_at)"
                      " VALUES (%s, %s, %s, %s)", (slug, slug, name, payload, NOW))

        # users：空才播種（既有帳號不動）
        x.execute("SELECT COUNT(*) FROM users")
        if x.fetchone()[0] == 0:
            email = (kv.get("ADMIN_EMAIL") or "office@tiri.tw").strip().lower()
            pw_hash = kv.get("ADMIN_PASS_HASH") or generate_password_hash(
                os.environ.get("ADMIN_PASS", "tiri1234"))
            nick = kv.get("ADMIN_NICKNAME") or "秘書處"
            x.execute("INSERT INTO users (email, password_hash, nickname, created_at)"
                      " VALUES (%s,%s,%s,%s)", (email, pw_hash, nick, NOW))

        x.execute("IF OBJECT_ID('settings','U') IS NOT NULL DROP TABLE settings")
        c.commit()

        report = []
        for t in ("submissions", "mail_settings", "mail_copy", "users"):
            x.execute(f"SELECT COUNT(*) FROM {t}")
            report.append(f"{t} {x.fetchone()[0]} 筆")
        x.execute("SELECT COUNT(*) FROM mail_copy WHERE copy_json IS NOT NULL")
        report.append(f"（其中 {x.fetchone()[0]} 筆有自訂文案）")
        print(f"{dbname}：{'、'.join(report)}，舊 settings 表已移除")
        c.close()


if __name__ == "__main__":
    main()
