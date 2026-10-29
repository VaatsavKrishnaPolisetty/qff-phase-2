"""Simple HTTP Server to launch the Emerging Genius Frontend Evaluation Hub."""

import http.server
import socketserver
import webbrowser
from pathlib import Path
import sys

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        frontend_dir = Path(__file__).resolve().parent / "frontend"
        super().__init__(*args, directory=str(frontend_dir), **kwargs)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            url = f"http://localhost:{PORT}"
            print("=" * 65)
            print(f"🚀 Emerging Genius QAOA Hub running at: {url}")
            print("   Press Ctrl+C to stop the server.")
            print("=" * 65)
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {PORT} already in use. Trying port 8081...")
            # Fallback to 8081
            with socketserver.TCPServer(("", 8081), Handler) as httpd:
                url = f"http://localhost:8081"
                print(f"🚀 Emerging Genius QAOA Hub running at: {url}")
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
                httpd.serve_forever()
        else:
            raise e

if __name__ == "__main__":
    run()
