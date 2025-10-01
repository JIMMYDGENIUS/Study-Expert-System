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
                hours = alloc.get("hours", 0)
                writer.writerow([daily.day, alloc.get("course", ""), hours])

        filename = f"{sanitize_filename(self._last.student_name)}_schedule.csv"
        return buf.getvalue().encode("utf-8"), filename

    def export_pdf(self) -> Tuple[Optional[bytes], str]:
        if not self._last:
            return None, "schedule.pdf"

        html_rows = ""
        for daily in self._last.schedule:
            for alloc in daily.allocations:
                course = alloc.get('course', '')
                hours = alloc.get('hours', 0)
                html_rows += f"<tr><td>{daily.day}</td><td>{course}</td><td>{hours}</td></tr>"

        html = f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <style>
                table,td,th {{
                    border:1px solid #333;
                    border-collapse:collapse;
                    padding:6px;
                }}
                th {{ background:#eee; }}
                table {{ width: 100%; table-layout: auto; }}
                h2 {{ margin: 0 0 4px 0; }}
                .sub {{ margin: 0 0 12px 0; font-size: 14px; }}
            </style>
        </head>
        <body>
            <h2>{self._last.student_name} Study Timetable</h2>
            <p class='sub'><b>Level:</b> {self._last.academic_level} &nbsp;&nbsp; 
               <b>Semester:</b> {self._last.semester}</p>
            <p><b>Total Weekly Hours:</b> {self._last.total_weekly_hours}</p>
            <table>
                <thead><tr><th>Day</th><th>Course</th><th>Hours</th></tr></thead>
                <tbody>{html_rows}</tbody>
            </table>
        </body>
        </html>
        """

        filename = f"{sanitize_filename(self._last.student_name)}_schedule.pdf"

        try:
            from weasyprint import HTML  # type: ignore
            pdf_bytes = HTML(string=html).write_pdf()
            return pdf_bytes, filename
        except Exception:
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas

                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=letter)
                width, height = letter
                textobject = c.beginText(40, height - 40)
                textobject.textLine("Study Schedule")
                textobject.textLine("")
                textobject.textLine(
                    f"Student: {self._last.student_name} | Level: {self._last.academic_level} | Semester: {self._last.semester}"
                )
                textobject.textLine(f"Total Weekly Hours: {self._last.total_weekly_hours}")
                textobject.textLine("")
                for daily in self._last.schedule:
                    for alloc in daily.allocations:
                        course = alloc.get('course', '')
                        hours = alloc.get('hours', 0)
                        line = f"{daily.day} | {course} | {hours}h"
                        textobject.textLine(line[:120])
                c.drawText(textobject)
                c.showPage()
                c.save()
                return buf.getvalue(), filename
            except Exception:
                return html.encode("utf-8"), filename
