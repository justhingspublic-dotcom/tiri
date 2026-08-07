# 一次性搬遷：把測試機（.env 的 DB_SERVER，現＝192.168.1.92）的 TIRI 庫搬到正式 SQL Server
# 正式機連線資訊讀 .env 的 PROD_DB_SERVER / PROD_DB_USER / PROD_DB_PASS（埠用「主機,1433」格式）
# 安全性：跑多次安全——目標表「空的才填」，絕不覆蓋正式機既有資料
# 預設不搬 submissions（測試收件）；要搬加 --with-submissions（保留原 id）
import argparse
import os
from pathlib import Path

import pymssql
from dotenv import load_dotenv

HERE = Path(__file__).parent
load_dotenv(HERE / ".env")

SRC = dict(server=os.environ["DB_SERVER"], user=os.environ["DB_USER"],
           password=os.environ["DB_PASS"])
DST = dict(server=os.environ["PROD_DB_SERVER"], user=os.environ["PROD_DB_USER"],
           password=os.environ["PROD_DB_PASS"])
DB = "TIRI"

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-submissions", action="store_true",
                    help="連 submissions（收件資料）一起搬，保留原 id")
    args = ap.parse_args()

    s = pymssql.connect(**SRC, database=DB, charset="UTF-8")
    sx = s.cursor(as_dict=True)

    # 正式機：建庫（不存在才建）→ 建表
    boot = pymssql.connect(**DST, autocommit=True)
    boot.cursor().execute(f"IF DB_ID('{DB}') IS NULL CREATE DATABASE {DB}")
    boot.close()
    d = pymssql.connect(**DST, database=DB, charset="UTF-8")
    dx = d.cursor()
    for ddl in DDL:
        dx.execute(ddl)
    d.commit()

    report = []

    # mail_settings：目標空才搬（一列式 id=1，含 smtp_pass 原樣帶過去）
    dx.execute("SELECT COUNT(*) FROM mail_settings")
    if dx.fetchone()[0] == 0:
        sx.execute("SELECT * FROM mail_settings WHERE id = 1")
        r = sx.fetchone()
        if r:
            dx.execute(
                "INSERT INTO mail_settings (id, smtp_host, smtp_port, smtp_user,"
                " smtp_pass, mail_to, dry_run, updated_at) VALUES (1,%s,%s,%s,%s,%s,%s,%s)",
                (r["smtp_host"], r["smtp_port"], r["smtp_user"], r["smtp_pass"],
                 r["mail_to"], 1 if r["dry_run"] else 0, r["updated_at"]))
            report.append("mail_settings 已搬")
    else:
        report.append("mail_settings 目標已有資料，略過")

    # mail_copy：缺哪筆補哪筆
    sx.execute("SELECT * FROM mail_copy")
    n = 0
    for r in sx.fetchall():
        dx.execute("SELECT COUNT(*) FROM mail_copy WHERE form_slug = %s", (r["form_slug"],))
        if dx.fetchone()[0] == 0:
            dx.execute("INSERT INTO mail_copy (form_slug, form_name, copy_json, updated_at)"
                       " VALUES (%s,%s,%s,%s)",
                       (r["form_slug"], r["form_name"], r["copy_json"], r["updated_at"]))
            n += 1
    report.append(f"mail_copy 補 {n} 筆")

    # users：目標空才搬（password_hash 原樣帶過去＝後台帳密不變）
    dx.execute("SELECT COUNT(*) FROM users")
    if dx.fetchone()[0] == 0:
        sx.execute("SELECT email, password_hash, nickname, created_at FROM users ORDER BY id")
        for r in sx.fetchall():
            dx.execute("INSERT INTO users (email, password_hash, nickname, created_at)"
                       " VALUES (%s,%s,%s,%s)",
                       (r["email"], r["password_hash"], r["nickname"], r["created_at"]))
        report.append("users 已搬")
    else:
        report.append("users 目標已有資料，略過")

    # submissions：預設不搬；--with-submissions 時目標空才搬（IDENTITY_INSERT 保 id）
    if args.with_submissions:
        dx.execute("SELECT COUNT(*) FROM submissions")
        if dx.fetchone()[0] == 0:
            sx.execute("SELECT * FROM submissions ORDER BY id")
            rows = sx.fetchall()
            if rows:
                dx.execute("SET IDENTITY_INSERT submissions ON")
                for r in rows:
                    dx.execute(
                        "INSERT INTO submissions (id, form_slug, form_name, page_url,"
                        " fields_json, ip, submitted_at, mail_status, deleted_at)"
                        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (r["id"], r["form_slug"], r["form_name"], r["page_url"],
                         r["fields_json"], r["ip"], r["submitted_at"],
                         r["mail_status"], r["deleted_at"]))
                dx.execute("SET IDENTITY_INSERT submissions OFF")
            report.append(f"submissions 已搬 {len(rows)} 筆")
        else:
            report.append("submissions 目標已有資料，略過")
    else:
        report.append("submissions 未搬（測試資料；要搬加 --with-submissions）")

    d.commit()

    # 驗證：印目標庫各表筆數
    dxd = d.cursor(as_dict=True)
    counts = []
    for t in ("submissions", "mail_settings", "mail_copy", "users"):
        dxd.execute(f"SELECT COUNT(*) n FROM {t}")
        counts.append(f"{t} {dxd.fetchone()['n']} 筆")
    print("搬遷結果：" + "、".join(report))
    print(f"正式機 {DST['server']} 的 {DB}：" + "、".join(counts))
    s.close()
    d.close()


if __name__ == "__main__":
    main()
