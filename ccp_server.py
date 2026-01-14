import argparse
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import parse_qs, urlparse

from ccp_storage import DEFAULT_DB_PATH, init_db, list_items


class CCPHandler(BaseHTTPRequestHandler):
    db_path: str = DEFAULT_DB_PATH

    def _send_response(self, content: str, status: int = 200, content_type: str = "text/html") -> None:
        encoded = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _parse_query(self):
        parsed = urlparse(self.path)
        return parsed.path, parse_qs(parsed.query)

    def do_GET(self):  # noqa: N802
        path, query = self._parse_query()
        if path == "/api/items":
            item_type = query.get("type", [None])[0]
            limit = int(query.get("limit", ["100"])[0])
            items = list_items(db_path=self.db_path, limit=limit, item_type=item_type)
            self._send_response(json.dumps(items), content_type="application/json")
            return

        if path == "/":
            item_type = query.get("type", [None])[0]
            items = list_items(db_path=self.db_path, limit=200, item_type=item_type)
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            filters = [
                ("All", None),
                ("Science", "science"),
                ("Society", "society"),
            ]
            filter_links = " ".join(
                f'<a class="filter" href="/?type={value}">{label}</a>'
                if value
                else '<a class="filter" href="/">All</a>'
                for label, value in filters
            )

            rows = []
            for item in items:
                summary = item.get("summary") or ""
                tone = item.get("tone")
                tone_display = f"{tone:.2f}" if isinstance(tone, (float, int)) else ""
                rows.append(
                    f"""
                    <div class="item">
                      <div class="meta">
                        <span class="badge">{item['item_type'].upper()}</span>
                        <span class="topic">{item['topic']}</span>
                        <span class="source">{item['source']}</span>
                        <span class="date">{item.get('published_date') or ""}</span>
                      </div>
                      <h3>{item['headline']}</h3>
                      <p class="summary">{summary}</p>
                      <div class="links">
                        <a href="{item.get('url') or '#'}" target="_blank" rel="noreferrer">Open source</a>
                        <button class="copy" data-copy="{item['headline']} — {summary} {item.get('url') or ''}">Copy</button>
                        <span class="tone">{tone_display}</span>
                      </div>
                    </div>
                    """
                )

            html = f"""
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Conscious Curation Pipeline</title>
                <style>
                  body {{
                    font-family: "Inter", Arial, sans-serif;
                    margin: 0;
                    padding: 24px;
                    background: #0f172a;
                    color: #e2e8f0;
                  }}
                  header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: baseline;
                    flex-wrap: wrap;
                    gap: 12px;
                  }}
                  h1 {{
                    margin: 0;
                    font-size: 24px;
                  }}
                  .filters {{
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                  }}
                  .filter {{
                    color: #94a3b8;
                    text-decoration: none;
                    border: 1px solid #334155;
                    padding: 6px 10px;
                    border-radius: 6px;
                  }}
                  .item {{
                    background: #111827;
                    border: 1px solid #1f2937;
                    border-radius: 12px;
                    padding: 16px;
                    margin-top: 16px;
                  }}
                  .meta {{
                    font-size: 12px;
                    text-transform: uppercase;
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                  }}
                  .badge {{
                    background: #2563eb;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 999px;
                    font-weight: 600;
                  }}
                  .summary {{
                    color: #cbd5f5;
                    font-size: 14px;
                  }}
                  .links {{
                    display: flex;
                    gap: 12px;
                    align-items: center;
                    flex-wrap: wrap;
                  }}
                  .links a {{
                    color: #38bdf8;
                    text-decoration: none;
                  }}
                  .copy {{
                    background: #1d4ed8;
                    border: none;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                  }}
                  .tone {{
                    color: #fbbf24;
                    font-size: 12px;
                  }}
                </style>
              </head>
              <body>
                <header>
                  <div>
                    <h1>Conscious Curation Pipeline</h1>
                    <p>Updated {now}</p>
                  </div>
                  <div class="filters">{filter_links}</div>
                </header>
                <main>
                  {''.join(rows) if rows else "<p>No items yet. Run the ingest job.</p>"}
                </main>
                <script>
                  document.querySelectorAll(".copy").forEach((button) => {{
                    button.addEventListener("click", () => {{
                      navigator.clipboard.writeText(button.dataset.copy || "");
                      button.textContent = "Copied!";
                      setTimeout(() => (button.textContent = "Copy"), 1200);
                    }});
                  }});
                </script>
              </body>
            </html>
            """
            self._send_response(html)
            return

        self._send_response("Not Found", status=404, content_type="text/plain")


def run_server(host: str, port: int, db_path: str) -> None:
    init_db(db_path)
    CCPHandler.db_path = db_path
    server = HTTPServer((host, port), CCPHandler)
    print(f"Serving CCP web UI on http://{host}:{port}")
    server.serve_forever()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Serve the CCP web UI.")
    parser.add_argument("--db-path", default=DEFAULT_DB_PATH, help="Path to the SQLite database.")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    return parser


if __name__ == "__main__":
    args = build_parser().parse_args()
    run_server(args.host, args.port, args.db_path)
