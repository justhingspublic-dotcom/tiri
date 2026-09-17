#!/usr/bin/env python3
"""Start/reuse the local TIRI review server and open the review page."""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import quote
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
import sys,subprocess,time,webbrowser
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
URL='http://localhost:4173/outputs/2026-09-17-v1-total-review-round2/'+quote('總複檢第二輪.html')
class Handler(SimpleHTTPRequestHandler):
 def end_headers(self):
  self.send_header('Cache-Control','no-store, must-revalidate')
  super().end_headers()
def ready():
 try:
  with urlopen('http://localhost:4173/v1/html/index.html',timeout=2) as r:return r.status==200 and 'TIRI' in r.read().decode('utf-8')
 except Exception:return False
if '--serve' in sys.argv:
 ThreadingHTTPServer(('127.0.0.1',4173),partial(Handler,directory=str(ROOT))).serve_forever()
else:
 if not ready():
  with (OUT/'preview-server.log').open('a') as log:
   process=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--serve'],cwd=ROOT,stdout=log,stderr=log,start_new_session=True)
  for _ in range(30):
   if ready():break
   if process.poll() is not None:raise SystemExit('無法啟動 4173 預覽，請查看同資料夾 preview-server.log。')
   time.sleep(.1)
 if not ready():raise SystemExit('預覽未能啟動，請查看 preview-server.log。')
 print(URL)
 if '--check' not in sys.argv:webbrowser.open(URL)
