from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import io
from datetime import datetime
from collections import defaultdict
import pytz

BLUE = colors.HexColor("#003087")
LIGHT_BLUE = colors.HexColor("#e8f0fe")
ALT_ROW = colors.HexColor("#f5f7ff")


def _dur(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m:02d}m"


def _table_style(n_data_rows: int) -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (0, 1), (0, -1), "LEFT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), LIGHT_BLUE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, ALT_ROW]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ])


def generate_report_pdf(entries: list, start_date, end_date, timezone_str: str = "America/New_York") -> bytes:
    tz = pytz.timezone(timezone_str)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        rightMargin=0.75 * inch, leftMargin=0.75 * inch,
        topMargin=inch, bottomMargin=inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("KTitle", parent=styles["Title"], fontSize=20, textColor=BLUE, spaceAfter=4)
    sub_style = ParagraphStyle("KSub", parent=styles["Normal"], fontSize=10, textColor=colors.grey, spaceAfter=2)
    emp_style = ParagraphStyle("KEmp", parent=styles["Heading2"], fontSize=14, textColor=BLUE, spaceAfter=4)

    # Group completed entries by employee
    by_emp: dict[str, list] = defaultdict(list)
    for e in entries:
        if e.get("clock_out"):
            by_emp[e["employee_name"]].append(e)

    story = []

    # ── Summary page ──────────────────────────────────────────────────────────
    story.append(Paragraph("Kumon Time Report", title_style))
    story.append(Paragraph(
        f"{start_date.strftime('%B %d, %Y')}  –  {end_date.strftime('%B %d, %Y')}",
        sub_style,
    ))
    story.append(Paragraph(
        f"Generated {datetime.now(tz).strftime('%B %d, %Y at %I:%M %p %Z')}",
        sub_style,
    ))
    story.append(Spacer(1, 0.3 * inch))

    grand_secs = 0.0
    summary_rows = [["Employee", "Total Hours", "Shifts"]]
    for name in sorted(by_emp):
        secs = sum(
            (datetime.fromisoformat(e["clock_out"]) - datetime.fromisoformat(e["clock_in"])).total_seconds()
            if isinstance(e["clock_in"], str) else
            (e["clock_out"] - e["clock_in"]).total_seconds()
            for e in by_emp[name]
        )
        grand_secs += secs
        summary_rows.append([name, _dur(secs), str(len(by_emp[name]))])
    summary_rows.append(["TOTAL", _dur(grand_secs), str(sum(len(v) for v in by_emp.values()))])

    t = Table(summary_rows, colWidths=[3 * inch, 2 * inch, 1.5 * inch])
    t.setStyle(_table_style(len(summary_rows) - 2))
    story.append(t)

    # ── Per-employee pages ─────────────────────────────────────────────────────
    for name in sorted(by_emp):
        story.append(PageBreak())
        emp_entries = sorted(
            by_emp[name],
            key=lambda e: e["clock_in"] if not isinstance(e["clock_in"], str) else datetime.fromisoformat(e["clock_in"])
        )

        story.append(Paragraph(name, emp_style))
        story.append(Paragraph(
            f"{start_date.strftime('%B %d, %Y')}  –  {end_date.strftime('%B %d, %Y')}",
            sub_style,
        ))
        story.append(Spacer(1, 0.2 * inch))

        detail_rows = [["Date", "Clock In", "Clock Out", "Duration"]]
        emp_secs = 0.0
        for e in emp_entries:
            ci = e["clock_in"] if not isinstance(e["clock_in"], str) else datetime.fromisoformat(e["clock_in"])
            co = e["clock_out"] if not isinstance(e["clock_out"], str) else datetime.fromisoformat(e["clock_out"])
            if ci.tzinfo is None:
                ci = pytz.utc.localize(ci)
            if co.tzinfo is None:
                co = pytz.utc.localize(co)
            ci_local = ci.astimezone(tz)
            co_local = co.astimezone(tz)
            secs = (co - ci).total_seconds()
            emp_secs += secs
            detail_rows.append([
                ci_local.strftime("%a, %b %d, %Y"),
                ci_local.strftime("%I:%M %p"),
                co_local.strftime("%I:%M %p"),
                _dur(secs),
            ])
        detail_rows.append(["", "", "TOTAL", _dur(emp_secs)])

        t2 = Table(detail_rows, colWidths=[2.5 * inch, 1.75 * inch, 1.75 * inch, 1.5 * inch])
        t2.setStyle(_table_style(len(detail_rows) - 2))
        story.append(t2)

    doc.build(story)
    return buf.getvalue()
