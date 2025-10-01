import React, { useState } from "react";

function App() {
  const [formData, setFormData] = useState({
    student_name: "",
    academic_level: "",
    semester: "",
    avg_hours_per_day: 4,
    courses: [],
  });

  const [schedule, setSchedule] = useState(null);

  // Add new course
  const addCourse = () => {
    setFormData((prev) => {
      const updated = {
        ...prev,
        courses: [
          ...prev.courses,
          { name: "", credit_unit: 3, confidence_level: 3 },
        ],
      };
      // Auto scroll to bottom after state updates in next tick
      setTimeout(() => {
        window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
      }, 0);
      return updated;
    });
  };

  // Update course
  const updateCourse = (index, key, value) => {
    const newCourses = [...formData.courses];
    newCourses[index][key] = value;
    setFormData({ ...formData, courses: newCourses });
  };

  // Submit to backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch("http://127.0.0.1:8000/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!res.ok) throw new Error("Failed to generate schedule");
      const data = await res.json();
      setSchedule(data);
    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="page">
      <div className="container">
        <h1 className="title">Exam Prep Expert System</h1>

        <form onSubmit={handleSubmit} className="card form">
          <div className="grid-2">
            <div className="form-group">
              <label className="label">Student Name</label>
              <input
                type="text"
                value={formData.student_name}
                onChange={(e) => setFormData({ ...formData, student_name: e.target.value })}
                className="input"
                required
              />
            </div>

            <div className="form-group">
              <label className="label">Academic Level</label>
              <input
                type="text"
                placeholder="e.g. 100L, 200L"
                value={formData.academic_level}
                onChange={(e) => setFormData({ ...formData, academic_level: e.target.value })}
                className="input"
                required
              />
            </div>

            <div className="form-group">
              <label className="label">Semester</label>
              <input
                type="text"
                placeholder="e.g. First Semester"
                value={formData.semester}
                onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                className="input"
                required
              />
            </div>

            <div className="form-group">
              <label className="label">Average Study Hours Per Day</label>
              <input
                type="number"
                min="1"
                max="24"
                step="0.5"
                value={formData.avg_hours_per_day}
                onChange={(e) =>
                  setFormData({ ...formData, avg_hours_per_day: Math.min(24, parseFloat(e.target.value) || 0) })
                }
                className="input"
                required
              />
            </div>
          </div>

          <div className="section">
            <div className="section-header">
              <h2 className="section-title">Courses</h2>
            </div>

            {formData.courses.map((course, ci) => (
              <div key={ci} className="course-card">
                <div className="grid-3">
                  <div className="form-group">
                    <label className="label">Course Name</label>
                    <input
                      type="text"
                      value={course.name}
                      onChange={(e) => updateCourse(ci, "name", e.target.value)}
                      className="input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="label">Credit Unit</label>
                    <input
                      type="number"
                      min="1"
                      value={course.credit_unit}
                      onChange={(e) => updateCourse(ci, "credit_unit", parseInt(e.target.value) || 1)}
                      className="input"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label className="label">Confidence Level (1-5)</label>
                    <input
                      type="number"
                      min="1"
                      max="5"
                      value={course.confidence_level}
                      onChange={(e) =>
                        updateCourse(ci, "confidence_level", Math.min(5, Math.max(1, parseInt(e.target.value) || 1)))
                      }
                      className="input"
                      required
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="actions">
            <div className="actions-left">
              <button type="button" onClick={addCourse} className="button button-primary">+ Add Course</button>
            </div>
            <div className="actions-right">
              <button type="submit" className="button button-accent">Generate Schedule</button>
            </div>
          </div>
        </form>

        {schedule && (
          <div className="card">
            <h2 className="section-title">{schedule.student_name} Study Timetable</h2>
            <p className="subtitle">Level: {schedule.academic_level} · Semester: {schedule.semester}</p>
            <table className="table">
              <thead>
                <tr>
                  <th>Day</th>
                  <th>Course</th>
                  <th>Hours</th>
                </tr>
              </thead>
              <tbody>
                {schedule.schedule.map((daily, di) => (
                  daily.allocations.map((alloc, ai) => (
                    <tr key={`${di}-${ai}`}>
                      {ai === 0 ? (
                        <td rowSpan={daily.allocations.length}>{daily.day}</td>
                      ) : null}
                      <td>{alloc.course}</td>
                      <td>{alloc.hours} hrs</td>
                    </tr>
                  ))
                ))}
              </tbody>
            </table>

            <div className="download-actions">
              <button type="button" className="button" onClick={async () => {
                const res = await fetch("http://127.0.0.1:8000/api/download/csv");
                if (!res.ok) return alert("No schedule available yet.");
                const { filename, content, mime } = await res.json();
                const blob = new Blob([content], { type: mime });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
              }}>Download CSV</button>

              <button type="button" className="button" onClick={async () => {
                const res = await fetch("http://127.0.0.1:8000/api/download/pdf");
                if (!res.ok) return alert("No schedule available yet.");
                const { filename, content_base64, mime } = await res.json();
                const byteChars = atob(content_base64);
                const byteNumbers = new Array(byteChars.length);
                for (let i = 0; i < byteChars.length; i++) byteNumbers[i] = byteChars.charCodeAt(i);
                const blob = new Blob([new Uint8Array(byteNumbers)], { type: mime });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
              }}>Download PDF</button>
            </div>

            {schedule.per_course_hours && (
              <div className="summary">
                <h3 className="summary-title">Weekly Hours per Course</h3>
                <ul className="summary-list">
                  {Object.entries(schedule.per_course_hours).map(([course, hours]) => (
                    <li key={course}>
                      <span className="chip">{course}</span>
                      <span>{hours} hrs</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
