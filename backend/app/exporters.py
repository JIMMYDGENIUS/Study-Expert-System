from __future__ import annotations

import io
import csv
import re
from typing import Optional, Tuple

from .models import GenerateResponse


def sanitize_filename(name: str) -> str:
    """Make a safe filename (no spaces, special chars)."""
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", name.strip())
    return safe or "student"


class ExportRegistry:
    def __init__(self) -> None:
        self._last: Optional[GenerateResponse] = None

    def store_last(self, resp: GenerateResponse) -> None:
        self._last = resp

    def export_csv(self) -> Tuple[Optional[bytes], str]:
        if not self._last:
            return None, "schedule.csv"

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Day", "Course", "Hours"])

        for daily in self._last.schedule:
            for alloc in daily.allocations:
                # Support both dict-like and pydantic model allocations
                course = getattr(alloc, "course", None)
                hours = getattr(alloc, "hours", None)
                if course is None and isinstance(alloc, dict):
                    course = alloc.get("course", "")
                if hours is None and isinstance(alloc, dict):
                    hours = alloc.get("hours", 0)
                writer.writerow([daily.day, course or "", hours or 0])

        filename = f"{sanitize_filename(self._last.student_name)}_schedule.csv"
        return buf.getvalue().encode("utf-8"), filename

    def export_pdf(self) -> Tuple[Optional[bytes], str]:
        if not self._last:
            return None, "schedule.pdf"
        filename = f"{sanitize_filename(self._last.student_name)}_schedule.pdf"

        # First try: ReportLab table (reliable PDF without extra deps)
        try:
            from reportlab.lib import colors  # type: ignore
            from reportlab.lib.pagesizes import A4  # type: ignore
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer  # type: ignore
            from reportlab.lib.styles import getSampleStyleSheet  # type: ignore

            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
            styles = getSampleStyleSheet()
            story = []

            title = Paragraph(f"<para align='center'><b>{self._last.student_name} Study Timetable</b></para>", styles['Title'])
            sub = Paragraph(
                f"<para align='center'>Level: {self._last.academic_level} &nbsp;&nbsp; Semester: {self._last.semester}</para>",
                styles['Normal']
            )
            meta = Paragraph(f"<para align='center'>Total Weekly Hours: {self._last.total_weekly_hours}</para>", styles['Normal'])
            story.extend([title, Spacer(1, 6), sub, meta, Spacer(1, 12)])

            data = [["Day", "Course", "Hours"]]
            row_spans = []  # collect (start_row, end_row, col) spans for 'Day'
            current_row = 1
            for daily in self._last.schedule:
                if not daily.allocations:
                    continue
                start = current_row
                for idx, alloc in enumerate(daily.allocations):
                    course = getattr(alloc, 'course', None)
                    hours = getattr(alloc, 'hours', None)
                    if course is None and isinstance(alloc, dict):
                        course = alloc.get('course', '')
                    if hours is None and isinstance(alloc, dict):
                        hours = alloc.get('hours', 0)
                    row = [daily.day if idx == 0 else "", course or '', f"{hours} hrs"]
                    data.append(row)
                    current_row += 1
                end = current_row - 1
                if end > start:
                    row_spans.append((start, end, 0))  # span Day column

            table = Table(data, colWidths=[100, 320, 70])
            style_cmds = [
                ('GRID', (0,0), (-1,-1), 0.6, colors.HexColor('#243055')),
                ('BACKGROUND', (0,0), (-1,0), colors.Color(1,1,1,0.05)),
                ('ALIGN', (0,0), (-1,0), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]
            for start, end, col in row_spans:
                style_cmds.append(('SPAN', (col, start), (col, end)))
                style_cmds.append(('FONTNAME', (col, start), (col, end), 'Helvetica-Bold'))
            table.setStyle(TableStyle(style_cmds))

            story.append(table)
            doc.build(story)
            return buf.getvalue(), filename
        except Exception:
            pass

        # Fallback: WeasyPrint (if installed)
        try:
            html_rows = ""
            for daily in self._last.schedule:
                if not daily.allocations:
                    continue
                first = True
                span = len(daily.allocations)
                for alloc in daily.allocations:
                    course = getattr(alloc, 'course', None)
                    hours = getattr(alloc, 'hours', None)
                    if course is None and isinstance(alloc, dict):
                        course = alloc.get('course', '')
                    if hours is None and isinstance(alloc, dict):
                        hours = alloc.get('hours', 0)
                    if first:
                        html_rows += f"<tr><td rowspan='{span}' class='day'>{daily.day}</td><td>{course}</td><td>{hours} hrs</td></tr>"
                        first = False
                    else:
                        html_rows += f"<tr><td>{course}</td><td>{hours} hrs</td></tr>"

            html = f"""
            <html>
            <head>
                <meta charset='utf-8'>
                <style>
                    :root {{ --bg:#0b1020; --surface:#121833; --surface2:#0f1530; --text:#e9ecf5; --muted:#9aa3b2; --border:#243055; }}
                    body {{ background: #0b1020; color: var(--text); font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }}
                    h2 {{ margin: 0 0 6px 0; text-align:center; }}
                    .sub, .meta {{ margin: 0 0 12px 0; font-size: 14px; color: var(--muted); text-align:center; }}
                    .meta {{ margin-top: -8px; }}
                    table {{ width: 100%; border-collapse: collapse; background: var(--surface); }}
                    th, td {{ border: 1px solid var(--border); padding: 8px 10px; text-align: left; }}
                    thead th {{ background: rgba(255,255,255,0.05); }}
                    td.day {{ font-weight: 600; background: rgba(255,255,255,0.02); }}
                </style>
            </head>
            <body>
                <h2>{self._last.student_name} Study Timetable</h2>
                <p class='sub'><b>Level:</b> {self._last.academic_level} &nbsp;&nbsp; <b>Semester:</b> {self._last.semester}</p>
                <p class='meta'><b>Total Weekly Hours:</b> {self._last.total_weekly_hours}</p>
                <table>
                    <thead><tr><th>Day</th><th>Course</th><th>Hours</th></tr></thead>
                    <tbody>{html_rows}</tbody>
                </table>
            </body>
            </html>
            """

            from weasyprint import HTML  # type: ignore
            pdf_bytes = HTML(string=html).write_pdf()
            return pdf_bytes, filename
        except Exception:
            # Last resort: simple text PDF
            try:
                from reportlab.lib.pagesizes import letter  # type: ignore
                from reportlab.pdfgen import canvas  # type: ignore
                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=letter)
                width, height = letter
                textobject = c.beginText(40, height - 40)
                textobject.textLine(f"{self._last.student_name} Study Timetable")
                textobject.textLine(f"Level: {self._last.academic_level} | Semester: {self._last.semester}")
                textobject.textLine(f"Total Weekly Hours: {self._last.total_weekly_hours}")
                textobject.textLine("")
                for daily in self._last.schedule:
                    for alloc in daily.allocations:
                        course = getattr(alloc, 'course', None)
                        hours = getattr(alloc, 'hours', None)
                        if course is None and isinstance(alloc, dict):
                            course = alloc.get('course', '')
                        if hours is None and isinstance(alloc, dict):
                            hours = alloc.get('hours', 0)
                        line = f"{daily.day} | {course} | {hours} hrs"
                        textobject.textLine(line[:120])
                c.drawText(textobject)
                c.showPage()
                c.save()
                return buf.getvalue(), filename
            except Exception:
                return None, filename
