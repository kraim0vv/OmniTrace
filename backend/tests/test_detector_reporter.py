import pytest

from app.core.detector import detect_entity
from app.core.models import Finding, FindingStatus, ScanStatus, ScanSummary, TargetType
from app.core.reporter import generate_csv_report, generate_html_report, generate_json_report


@pytest.mark.parametrize(
    "query, expected_type, normalized",
    [
        ("1.1.1.1", TargetType.IP, "1.1.1.1"),
        ("2606:4700:4700::1111", TargetType.IP, "2606:4700:4700::1111"),
        ("Contact@Example.COM", TargetType.EMAIL, "contact@example.com"),
        ("https://Python.org/about", TargetType.DOMAIN, "python.org"),
        ("+380 (44) 123-45-67", TargetType.PHONE, "+380441234567"),
        ("@torvalds", TargetType.USERNAME, "torvalds"),
        ("d41d8cd98f00b204e9800998ecf8427e", TargetType.HASH, "d41d8cd98f00b204e9800998ecf8427e"),
    ],
)
def test_detect_entity(query, expected_type, normalized):
    result = detect_entity(query)
    assert result.detected_type == expected_type
    assert result.normalized_value == normalized


def _summary(target="victim"):
    return ScanSummary(
        scan_id="0123456789abcdef", target=target, target_type=TargetType.USERNAME,
        status=ScanStatus.COMPLETED, started_at=0,
    )


def _finding(**kwargs):
    base = dict(
        scan_id="0123456789abcdef", target="victim", target_type=TargetType.USERNAME,
        category="Social", source="Example", status=FindingStatus.FOUND,
    )
    base.update(kwargs)
    return Finding(**base)


def test_html_report_escapes_untrusted_values():
    payload = "<img src=x onerror=alert(1)>"
    html = generate_html_report(
        _summary(payload),
        [
            _finding(title=payload, description=payload, source=payload, url="https://e.com/?a=<b>"),
            _finding(url="javascript:alert(1)"),
        ],
    )
    assert "<img src=x" not in html
    assert "&lt;img src=x onerror=alert(1)&gt;" in html
    assert "href='javascript:" not in html


def test_json_and_csv_reports():
    findings = [_finding(title="Profile", url="https://example.com/victim")]
    assert '"integrity_sha256"' in generate_json_report(_summary(), findings)
    csv_text = generate_csv_report(findings)
    assert csv_text.splitlines()[0].startswith("ID,Timestamp,Target")
    assert "https://example.com/victim" in csv_text
