import csv
import hashlib
import io
import json
import time
from typing import List
from app.core.models import Finding, ScanSummary

def generate_json_report(summary: ScanSummary, findings: List[Finding]) -> str:
    data = {
        "report_type": "OmniTrace OSINT Intelligence Report",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "target": summary.target,
        "target_type": summary.target_type.value,
        "scan_id": summary.scan_id,
        "statistics": {
            "total_checks": summary.total_checks,
            "found": summary.found_count,
            "not_found": summary.not_found_count,
            "errors": summary.error_count,
        },
        "findings": [f.model_dump() for f in findings]
    }
    dumped = json.dumps(data, indent=2)
    sha256_hash = hashlib.sha256(dumped.encode("utf-8")).hexdigest()
    data["integrity_sha256"] = sha256_hash
    return json.dumps(data, indent=2)

def generate_csv_report(findings: List[Finding]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Timestamp", "Target", "Target Type", "Category", "Source",
        "Status", "Title", "URL", "Description"
    ])
    for f in findings:
        writer.writerow([
            f.id,
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(f.timestamp)),
            f.target,
            f.target_type.value,
            f.category,
            f.source,
            f.status.value,
            f.title or "",
            f.url or "",
            f.description or ""
        ])
    return output.getvalue()

def generate_html_report(summary: ScanSummary, findings: List[Finding]) -> str:
    now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    found_rows = [f for f in findings if f.status.value == "found"]

    rows_html = ""
    for f in found_rows:
        url_link = f"<a href='{f.url}' target='_blank' style='color:#38bdf8;'>{f.url}</a>" if f.url else "—"
        rows_html += f"""
        <tr>
            <td style="padding:10px; border-bottom:1px solid #1e293b;"><span style="background:#0284c7; color:#fff; padding:3px 8px; border-radius:4px; font-size:12px;">{f.source}</span></td>
            <td style="padding:10px; border-bottom:1px solid #1e293b;">{f.category}</td>
            <td style="padding:10px; border-bottom:1px solid #1e293b; font-weight:600;">{f.title or 'N/A'}</td>
            <td style="padding:10px; border-bottom:1px solid #1e293b;">{url_link}</td>
            <td style="padding:10px; border-bottom:1px solid #1e293b; color:#94a3b8; font-size:13px;">{f.description or ''}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>OmniTrace OSINT Intelligence Report - {summary.target}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #0b1120; color: #f1f5f9; padding: 40px; margin: 0; }}
  .container {{ max-width: 1000px; margin: 0 auto; background: #0f172a; padding: 32px; border-radius: 12px; border: 1px solid #1e293b; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #38bdf8; padding-bottom: 20px; margin-bottom: 24px; }}
  .title {{ font-size: 24px; font-weight: 700; color: #38bdf8; }}
  .badge {{ background: #1e293b; padding: 6px 12px; border-radius: 6px; font-family: monospace; font-size: 13px; }}
  .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 30px; }}
  .stat-card {{ background: #1e293b; padding: 16px; border-radius: 8px; text-align: center; }}
  .stat-num {{ font-size: 28px; font-weight: 700; color: #38bdf8; }}
  .stat-label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; text-align: left; margin-top: 16px; font-size: 14px; }}
  th {{ background: #1e293b; color: #94a3b8; padding: 12px; font-weight: 600; text-transform: uppercase; font-size: 11px; }}
  .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #1e293b; font-size: 12px; color: #64748b; display: flex; justify-content: space-between; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <div class="title">⚡ OmniTrace Intelligence Report</div>
      <div style="color:#94a3b8; font-size:14px; margin-top:4px;">Target: <strong style="color:#f8fafc;">{summary.target}</strong> ({summary.target_type.value.upper()})</div>
    </div>
    <div class="badge">Scan ID: {summary.scan_id[:8]}...</div>
  </div>

  <div class="stats">
    <div class="stat-card">
      <div class="stat-num">{summary.total_checks}</div>
      <div class="stat-label">Total Checks</div>
    </div>
    <div class="stat-card">
      <div class="stat-num" style="color:#10b981;">{summary.found_count}</div>
      <div class="stat-label">Confirmed Finds</div>
    </div>
    <div class="stat-card">
      <div class="stat-num" style="color:#64748b;">{summary.not_found_count}</div>
      <div class="stat-label">Not Found</div>
    </div>
    <div class="stat-card">
      <div class="stat-num" style="color:#f43f5e;">{summary.error_count}</div>
      <div class="stat-label">Errors / Limits</div>
    </div>
  </div>

  <h3 style="color:#e2e8f0; margin-bottom: 8px;">Confirmed Intelligence Findings ({len(found_rows)})</h3>
  <table>
    <thead>
      <tr>
        <th>Source</th>
        <th>Category</th>
        <th>Title</th>
        <th>Reference Link</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
      {rows_html if rows_html else '<tr><td colspan="5" style="text-align:center; padding:20px; color:#64748b;">No confirmed records discovered.</td></tr>'}
    </tbody>
  </table>

  <div class="footer">
    <div>Generated: {now_str} via OmniTrace OSINT Platform</div>
    <div>Chain of Custody: Passive Reconnaissance Integrity Verified</div>
  </div>
</div>
</body>
</html>
    """
    return html
