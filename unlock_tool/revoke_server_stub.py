#!/usr/bin/env python3
"""Simple HTTP server stub hosting a static revoke.txt file."""

import http.server
import socketserver
from pathlib import Path

PORT = 8000
ROOT_DIR = Path(__file__).resolve().parent
REVOKE_FILE = ROOT_DIR / 'revoke.txt'


class RevokeRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.strip('/') == 'revoke.txt':
            return str(REVOKE_FILE)
        return super().translate_path(path)


def main():
    if not REVOKE_FILE.exists():
        REVOKE_FILE.write_text('# Add revoked license IDs here\n', encoding='utf-8')
    with socketserver.TCPServer(('', PORT), RevokeRequestHandler) as httpd:
        print(f'Revoke server running at http://localhost:{PORT}/revoke.txt')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('Shutting down revoke server.')
            httpd.server_close()


if __name__ == '__main__':
    main()
