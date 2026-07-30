# 忘記後台密碼時用：直接重設管理員密碼（連線資訊讀 .env）
# 用法：.venv/bin/python reset_password.py 新密碼
#   - 本機跑會重設 .env 裡 DB_NAME 指到的庫（開發＝TIRI_dev）
#   - 要重設正式站：加參數 --db TIRI
import os
import sys
from pathlib import Path

import pymssql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv(Path(__file__).parent / ".env")

args = [a for a in sys.argv[1:] if not a.startswith("--")]
dbname = sys.argv[sys.argv.index("--db") + 1] if "--db" in sys.argv else os.environ.get("DB_NAME", "TIRI")
if not args or len(args[0]) < 8:
    print("用法：python reset_password.py 新密碼（至少 8 個字元）[--db TIRI]")
    sys.exit(1)

conn = pymssql.connect(server=os.environ["DB_SERVER"], user=os.environ["DB_USER"],
                       password=os.environ["DB_PASS"], database=dbname, charset="UTF-8")
cur = conn.cursor()
cur.execute("SELECT TOP 1 id, email FROM users ORDER BY id")
row = cur.fetchone()
if not row:
    print(f"{dbname} 的 users 表是空的，沒有帳號可重設")
    sys.exit(1)
cur.execute("UPDATE users SET password_hash = %s WHERE id = %s",
            (generate_password_hash(args[0]), row[0]))
conn.commit()
conn.close()
print(f"已重設 {dbname} 的管理員密碼（帳號 {row[1]}），現在就能用新密碼登入。")
