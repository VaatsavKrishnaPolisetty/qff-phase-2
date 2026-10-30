import os
import re
import subprocess
from pathlib import Path
import markdown

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def build_pdf_report():
    report_md_path = PROJECT_ROOT / "report.md"
    report_html_path = PROJECT_ROOT / "report.html"
    report_pdf_path = PROJECT_ROOT / "report.pdf"
    frontend_pdf_path = PROJECT_ROOT / "frontend" / "report.pdf"

    with open(report_md_path, "r", encoding="utf-8") as f:
        raw_md = f.read()

    # Protect Math blocks from markdown parser underscores and asterisks
    math_tokens = []
    def repl_display_math(m):
        idx = len(math_tokens)
        math_tokens.append(m.group(0))
        return f"%%MATH_DISP_{idx}%%"

    def repl_inline_math(m):
        idx = len(math_tokens)
        math_tokens.append(m.group(0))
        return f"%%MATH_INL_{idx}%%"

    # 1. Replace display math ($$...$$)
    protected_md = re.sub(r'(\$\$[\s\S]*?\$\$)', repl_display_math, raw_md)
    # 2. Replace inline math ($...$)
    protected_md = re.sub(r'(\$(?:\\\$|[^\$\n])+?\$)', repl_inline_math, protected_md)

    # 3. Convert markdown to HTML
    html_body = markdown.markdown(protected_md, extensions=['tables', 'fenced_code'])

    # 4. Restore math tokens
    for idx, token in enumerate(math_tokens):
        html_body = html_body.replace(f"%%MATH_DISP_{idx}%%", token)
        html_body = html_body.replace(f"%%MATH_INL_{idx}%%", token)

    # Wrap tables in overflow containers
    html_body = re.sub(r'(<table>[\s\S]*?</table>)', r'<div class="table-container">\1</div>', html_body)

    template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>QFF 2026 Phase 2 Technical Report — Emerging Genius</title>
  
  <script>
    window.MathJax = {
      tex: {
        inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
        displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
      },
      svg: { fontCache: 'global' },
      startup: {
        typeset: true
      }
    };
  </script>
  <script type="text/javascript" id="MathJax-script" async
    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
  </script>

  <style>
    @page {
      size: A4 portrait;
      margin: 1.2cm 1.2cm 1.5cm 1.2cm;
      @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-family: system-ui, -apple-system, sans-serif;
        font-size: 8pt;
        color: #64748b;
      }
    }

    * {
      box-sizing: border-box;
    }

    html, body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 9.2pt;
      line-height: 1.45;
      color: #1e293b;
      background: #ffffff;
      margin: 0;
      padding: 0;
      width: 100%;
    }

    /* Headings */
    h1 {
      font-size: 19pt;
      font-weight: 800;
      color: #0f172a;
      border-bottom: 2pt solid #0284c7;
      padding-bottom: 5px;
      margin-top: 0;
      margin-bottom: 10px;
      page-break-after: avoid;
    }

    h2 {
      font-size: 13pt;
      font-weight: 700;
      color: #0369a1;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 3px;
      margin-top: 18px;
      margin-bottom: 8px;
      page-break-after: avoid;
    }

    h3 {
      font-size: 10.5pt;
      font-weight: 600;
      color: #0f172a;
      margin-top: 14px;
      margin-bottom: 6px;
      page-break-after: avoid;
    }

    h4, h5 {
      font-size: 9.5pt;
      font-weight: 600;
      color: #334155;
      margin-top: 10px;
      margin-bottom: 4px;
      page-break-after: avoid;
    }

    p, li {
      text-align: justify;
      hyphens: auto;
      margin-top: 0;
      margin-bottom: 6px;
    }

    ul, ol {
      margin-top: 2px;
      margin-bottom: 6px;
      padding-left: 18px;
    }

    li {
      margin-bottom: 2px;
    }

    hr {
      border: 0;
      border-top: 1px solid #cbd5e1;
      margin: 12px 0;
    }

    /* Code and Pre blocks */
    code {
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      font-size: 7.8pt;
      background-color: #f1f5f9;
      color: #0f172a;
      padding: 1px 3.5px;
      border-radius: 3px;
      border: 1px solid #e2e8f0;
    }

    pre {
      background-color: #0f172a;
      color: #f8fafc;
      padding: 8px 10px;
      border-radius: 5px;
      overflow-x: auto;
      font-size: 7.2pt;
      line-height: 1.35;
      margin: 8px 0;
      page-break-inside: avoid;
    }

    pre code {
      background-color: transparent;
      color: inherit;
      padding: 0;
      border: none;
      font-size: inherit;
    }

    /* ======================================================= */
    /* TABLES: Bulletproof width containment & formatting      */
    /* ======================================================= */
    .table-container {
      width: 100% !important;
      max-width: 100% !important;
      margin: 10px 0 !important;
      overflow-x: hidden !important;
      page-break-inside: avoid;
    }

    table {
      width: 100% !important;
      max-width: 100% !important;
      border-collapse: collapse !important;
      font-size: 7.2pt !important;
      line-height: 1.25 !important;
      table-layout: fixed !important;
      word-wrap: break-word !important;
      overflow-wrap: break-word !important;
    }

    th, td {
      border: 0.5pt solid #cbd5e1 !important;
      padding: 4px 5px !important;
      vertical-align: middle !important;
      word-break: normal !important;
      overflow-wrap: break-word !important;
      hyphens: auto;
    }

    th {
      background-color: #f1f5f9 !important;
      color: #0f172a !important;
      font-weight: 700 !important;
      text-align: center !important;
    }

    tr:nth-child(even) td {
      background-color: #f8fafc;
    }

    /* ======================================================= */
    /* IMAGES: Perfectly fitted & centered without margin bleed */
    /* ======================================================= */
    img {
      max-width: 96% !important;
      max-height: 18cm !important;
      height: auto !important;
      display: block !important;
      margin: 12px auto !important;
      border-radius: 6px !important;
      border: 1px solid #cbd5e1 !important;
      page-break-inside: avoid;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    p > img {
      margin-bottom: 4px !important;
    }

    /* Print media adjustments */
    @media print {
      body {
        background: transparent;
      }
      a {
        color: #0369a1;
        text-decoration: none;
      }
      .no-print {
        display: none;
      }
    }
  </style>
</head>
<body>
__HTML_BODY__
</body>
</html>
"""

    full_html = template.replace("__HTML_BODY__", html_body)

    with open(report_html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Wrote HTML report to: {report_html_path}")

    # Compile PDF via Chrome Headless
    chrome_cmd = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "--headless=new",
        "--disable-gpu",
        "--virtual-time-budget=10000",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={report_pdf_path}",
        str(report_html_path)
    ]
    print("Compiling PDF with Google Chrome...")
    subprocess.run(chrome_cmd, check=True)
    print(f"Successfully compiled PDF to: {report_pdf_path}")

    # Copy to frontend/
    if frontend_pdf_path.parent.exists():
        import shutil
        shutil.copy2(report_pdf_path, frontend_pdf_path)
        print(f"Synced PDF to frontend at: {frontend_pdf_path}")

if __name__ == "__main__":
    build_pdf_report()
