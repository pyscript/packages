# ---------------------------------------------------------------------
# Broadcasting: combining arrays of different (but compatible) shapes.
# ---------------------------------------------------------------------

heading("Broadcasting: per-student exam scores")
note(
    "Five students sit four exams. We'll center each exam around its "
    "mean, then convert to letter grades, all without writing a loop."
)

students = ["Ada", "Brij", "Cleo", "Dax", "Esi"]
exams = ["Algebra", "Biology", "Chemistry", "Drama"]

# A 5x4 matrix: rows are students, columns are exams.
scores = rng.integers(50, 100, size=(len(students), len(exams)))
display(scores, append=True)

# Per-exam mean has shape (4,). Subtracting it from a (5, 4) array
# broadcasts the row across all five students.
exam_means = scores.mean(axis=0)
note(f"Per-exam means (shape {exam_means.shape}):")
display(exam_means.round(2), append=True)

centered = scores - exam_means
note("Scores centered on each exam's mean (shape stays 5\u00d74):")
display(centered.round(2), append=True)

# Grade thresholds via np.where, applied element-wise to the whole array.
heading("Element-wise classification with np.where")
grades = np.where(scores >= 85, "A",
          np.where(scores >= 70, "B",
          np.where(scores >= 60, "C", "D")))
display(grades, append=True)

# ---------------------------------------------------------------------
# Reshape and aggregate along axes.
# ---------------------------------------------------------------------

heading("Reshape and axis-wise reductions")
note(
    "Per-student mean uses <code>axis=1</code> (collapse columns). "
    "Per-exam mean uses <code>axis=0</code> (collapse rows)."
)

per_student = scores.mean(axis=1).round(2)
per_exam = scores.mean(axis=0).round(2)

note("Per-student means:")
display(dict(zip(students, per_student.tolist())), append=True)
note("Per-exam means:")
display(dict(zip(exams, per_exam.tolist())), append=True)

# A heat-map style visualization of the centered scores.
fig, ax = plt.subplots(figsize=(7, 3.5))
im = ax.imshow(centered, cmap="RdBu_r", vmin=-25, vmax=25, aspect="auto")
ax.set_xticks(range(len(exams)), exams)
ax.set_yticks(range(len(students)), students)
ax.set_title("Score relative to exam mean")
for i in range(centered.shape[0]):
    for j in range(centered.shape[1]):
        ax.text(j, i, f"{centered[i, j]:+.0f}",
                ha="center", va="center", color="black", fontsize=9)
fig.colorbar(im, ax=ax, label="\u0394 from mean")
fig.tight_layout()
display(fig, append=True)
