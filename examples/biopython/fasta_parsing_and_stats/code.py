# ---------------------------------------------------------------------
# Reading and writing FASTA: a tiny pretend transcriptome.
# ---------------------------------------------------------------------


from io import StringIO
import matplotlib.pyplot as plt
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqUtils import gc_fraction


heading("Parsing a FASTA file from a string")
note(
    "In real work you'd open a .fasta file, but `SeqIO.parse` accepts "
    "any text-mode handle, including an in-memory StringIO. Here we "
    "process five fictional transcripts."
)

fasta_text = """>TR001 ribosomal protein
ATGGCTAAAGTTCTGAACGTTGCCCTGAAAGGCAAGGTGGTTGCTGTAACCAACTGCTAA
>TR002 heat shock protein fragment
ATGAGCAAGGAAATCGTGCATCGCCTGAACAGCCTGGAGAAGGTAGCCAAGGCCCAATAA
>TR003 short hypothetical
ATGGGGTGCATCTAA
>TR004 transcription factor
ATGGAAGACTTCCAGCGCATGCTGGAGCGCTACAAGGAAAACGGCATCGAGCTGTAA
>TR005 polyA-rich tail example
ATGCCCAAATTTGGGAAATTTGGGAAATTTGGGAAATTTGGGAAATTTGGGAAATAA
"""

# SeqIO.parse returns an iterator of SeqRecord objects.
records = list(SeqIO.parse(StringIO(fasta_text), "fasta"))
note(f"Loaded <strong>{len(records)}</strong> records.")

# Compute simple stats per record.
rows = []
for r in records:
    rows.append({
        "id": r.id,
        "description": r.description,
        "length": len(r.seq),
        "gc_pct": round(gc_fraction(r.seq) * 100, 1),
        "first_protein": str(r.seq.translate(to_stop=True)),
    })

# Render as an HTML table.
header = "<tr>" + "".join(
    f"<th style='padding:4px 8px;text-align:left'>{c}</th>"
    for c in ["id", "length", "GC %", "translated (to stop)"]
) + "</tr>"
body = ""
for row in rows:
    body += (
        "<tr>"
        f"<td style='padding:4px 8px'><code>{row['id']}</code></td>"
        f"<td style='padding:4px 8px'>{row['length']}</td>"
        f"<td style='padding:4px 8px'>{row['gc_pct']}</td>"
        f"<td style='padding:4px 8px'><code>{row['first_protein']}</code></td>"
        "</tr>"
    )
display(HTML(f"<table>{header}{body}</table>"), append=True)

heading("Visualising GC content across records")
fig, ax = plt.subplots(figsize=(8, 3.5))
ids = [r["id"] for r in rows]
gc = [r["gc_pct"] for r in rows]
ax.bar(ids, gc, color="seagreen")
ax.set_ylabel("GC content (%)")
ax.set_title("GC content per transcript")
ax.set_ylim(0, 100)
fig.tight_layout()
display(fig, append=True)

heading("Writing FASTA back out")
note(
    "`SeqIO.write` accepts any iterable of SeqRecord objects and a "
    "destination handle. Here we filter to records longer than 30 bp "
    "and serialise them to a string."
)

long_records = [r for r in records if len(r.seq) > 30]
out_handle = StringIO()
SeqIO.write(long_records, out_handle, "fasta")
display(HTML(f"<pre>{out_handle.getvalue()}</pre>"), append=True)
