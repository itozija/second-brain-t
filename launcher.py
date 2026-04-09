#!/usr/bin/env python3
"""
Second Brain T — Web Launcher
Double-click or run: python3 launcher.py
Opens in your browser — no installation needed.
"""

import http.server
import threading
import webbrowser
import subprocess
import json
import sys
import os
from pathlib import Path

PORT = 7432
SCRIPT = Path(__file__).parent / 'build.py'
OUT = Path(__file__).parent / 'output'

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Second Brain T</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       background: #0d1117; color: #e6edf3; min-height: 100vh;
       display: flex; align-items: center; justify-content: center; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 14px;
        padding: 40px; width: 480px; }
h1 { font-size: 24px; font-weight: 700; text-align: center; margin-bottom: 6px; }
.sub { text-align: center; color: #8b949e; font-size: 13px; margin-bottom: 32px; }
label { font-size: 12px; color: #8b949e; display: block; margin-bottom: 6px; font-weight: 500; }
.row { margin-bottom: 18px; }
.input-row { display: flex; gap: 10px; }
input[type=text] { flex: 1; padding: 10px 14px; background: #21262d;
                   border: 1px solid #30363d; border-radius: 8px;
                   color: #e6edf3; font-size: 14px; outline: none; }
input[type=text]:focus { border-color: #388bfd; }
input[type=text]::placeholder { color: #484f58; }
.btn { padding: 10px 18px; border-radius: 8px; font-size: 13px;
       font-weight: 600; cursor: pointer; border: none; transition: opacity .15s; }
.btn:hover { opacity: .85; }
.btn-pick { background: #21262d; color: #e6edf3; border: 1px solid #30363d; }
.btn-run { background: #388bfd; color: white; width: 100%; padding: 13px;
           font-size: 15px; margin-top: 6px; }
.btn-run:disabled { opacity: .5; cursor: not-allowed; }
.check-row { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #c9d1d9; }
input[type=checkbox] { accent-color: #388bfd; width: 15px; height: 15px; }
#log { background: #010409; border-radius: 8px; padding: 14px;
       font-family: 'Menlo', monospace; font-size: 12px; height: 160px;
       overflow-y: auto; margin-top: 20px; display: none; }
.log-line { margin: 2px 0; }
.ok  { color: #3fb950; }
.err { color: #f85149; }
.inf { color: #388bfd; }
.dim { color: #8b949e; }
#open-btn { display: none; background: #3fb950; color: white; width: 100%;
            padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 600;
            cursor: pointer; border: none; margin-top: 10px; }
</style>
</head>
<body>
<div class="card">
  <h1>🧠 Second Brain T</h1>
  <p class="sub">Turn any folder into a knowledge base</p>

  <div class="row">
    <label>Folder</label>
    <div class="input-row">
      <input type="text" id="folder" placeholder="Paste your folder path here..." />
    </div>
  </div>

  <div class="row">
    <label>Title <span style="color:#484f58">(optional)</span></label>
    <input type="text" id="title" placeholder="e.g. My Research" style="width:100%" />
  </div>

  <div class="row">
    <div class="check-row" style="margin-bottom:8px">
      <input type="checkbox" id="cache" checked />
      <span>Use cache — skip files that haven't changed (faster)</span>
    </div>
    <div class="check-row">
      <input type="checkbox" id="clear" />
      <span>Clear previous output and start fresh</span>
    </div>
  </div>

  <button class="btn btn-run" id="run-btn" onclick="run()">▶ Run</button>
  <div id="log"></div>
  <button id="open-btn" onclick="openDash()">Open Dashboard →</button>
</div>

<script>
async function run() {
  const folder = document.getElementById('folder').value.trim();
  if (!folder) { alert('Please enter a folder path first.'); return; }

  const btn = document.getElementById('run-btn');
  btn.disabled = true; btn.textContent = 'Running...';
  document.getElementById('open-btn').style.display = 'none';

  const log = document.getElementById('log');
  log.style.display = 'block'; log.innerHTML = '';

  const params = new URLSearchParams({
    folder,
    title: document.getElementById('title').value.trim(),
    cache: document.getElementById('cache').checked ? '1' : '0',
    clear: document.getElementById('clear').checked ? '1' : '0'
  });

  const res = await fetch('/run?' + params);
  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const text = decoder.decode(value);
    for (const line of text.split('\\n')) {
      if (!line.trim()) continue;
      const cls = line.includes('✓') || line.includes('Done') ? 'ok'
                : line.includes('rror') ? 'err'
                : line.startsWith('  ') ? 'inf' : 'dim';
      const d = document.createElement('div');
      d.className = 'log-line ' + cls;
      d.textContent = line;
      log.appendChild(d);
      log.scrollTop = log.scrollHeight;
    }
  }

  btn.disabled = false; btn.textContent = '▶ Run Again';
  document.getElementById('open-btn').style.display = 'block';
}

function openDash() {
  window.open('/dashboard', '_blank');
}
</script>
</body>
</html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass  # suppress request logs

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(self.path)

        if parsed.path == '/':
            self._send(200, 'text/html', HTML.encode())

        elif parsed.path == '/run':
            params = parse_qs(parsed.query)
            folder = params.get('folder', [''])[0]
            title  = params.get('title',  [''])[0]
            cache  = params.get('cache',  ['1'])[0] == '1'

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()

            clear = params.get('clear', ['0'])[0] == '1'
            cmd = [sys.executable, str(SCRIPT), folder]
            if title: cmd += ['--title', title]
            if not cache: cmd.append('--no-cache')
            cmd.append('--clear' if clear else '--update')

            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    chunk = line.encode('utf-8')
                    self.wfile.write(f'{len(chunk):X}\r\n'.encode())
                    self.wfile.write(chunk + b'\r\n')
                    self.wfile.flush()
                proc.wait()
            except Exception as e:
                msg = f'Error: {e}\n'.encode()
                self.wfile.write(f'{len(msg):X}\r\n'.encode())
                self.wfile.write(msg + b'\r\n')
            self.wfile.write(b'0\r\n\r\n')

        elif parsed.path == '/dashboard':
            dash = OUT / 'index.html'
            if dash.exists():
                self._send(200, 'text/html', dash.read_bytes())
            else:
                self._send(404, 'text/plain', b'No output yet - run the tool first.')

        else:
            self._send(404, 'text/plain', b'Not found')

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    url = f'http://localhost:{PORT}'
    print(f'\n🧠 Second Brain T launcher running at {url}')
    print('   Opening in browser...\n')
    threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')


if __name__ == '__main__':
    main()
