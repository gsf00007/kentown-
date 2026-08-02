import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / 'index.html'
STATE_FILE = ROOT / 'admin-state.json'


def write_state_to_source(payload):
    text = INDEX.read_text(encoding='utf-8')
    state_script = '<script id="kentown-admin-state">\nwindow.__KENTOWN_ADMIN_STATE__ = ' + json.dumps(payload, indent=2) + ';\n</script>'
    pattern = re.compile(r'<script id="kentown-admin-state">.*?</script>', re.S)
    if pattern.search(text):
        text = pattern.sub(state_script, text, count=1)
    else:
        marker = '<script>\n/* ================= Kentown Mini Mart — App Logic ================= */'
        if marker in text:
            text = text.replace(marker, state_script + '\n' + marker, 1)
        else:
            text = text.replace('</body>', state_script + '\n</body>', 1)
    INDEX.write_text(text, encoding='utf-8')


class Handler(BaseHTTPRequestHandler):
    def _send_no_cache_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/api/admin-state':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_no_cache_headers()
            self.end_headers()
            if STATE_FILE.exists():
                self.wfile.write(STATE_FILE.read_bytes())
            else:
                self.wfile.write(b'{}')
            return
        if path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self._send_no_cache_headers()
            self.end_headers()
            self.wfile.write(INDEX.read_bytes())
            return
        if path.startswith('/'):
            path = ROOT / path.lstrip('/')
            if path.exists() and path.is_file():
                self.send_response(200)
                content_type = 'text/html; charset=utf-8' if path.suffix.lower() in {'.html', '.htm'} else 'application/octet-stream'
                self.send_header('Content-Type', content_type)
                self._send_no_cache_headers()
                self.end_headers()
                self.wfile.write(path.read_bytes())
                return
        self.send_response(404)
        self._send_no_cache_headers()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/save-state':
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length).decode('utf-8')
            try:
                payload = json.loads(body)
            except Exception:
                self.send_response(400)
                self._send_no_cache_headers()
                self.end_headers()
                return
            STATE_FILE.write_text(json.dumps(payload, indent=2))
            write_state_to_source(payload)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_no_cache_headers()
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return
        self.send_response(404)
        self._send_no_cache_headers()
        self.end_headers()

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 8000), Handler)
    print('Serving at http://127.0.0.1:8000')
    server.serve_forever()
