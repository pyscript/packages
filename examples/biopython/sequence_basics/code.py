"""
A first taste of Biopython: working with biological sequences.

Biopython's `Seq` object behaves a lot like a Python string, but it
also knows about biology: complement, reverse complement, transcription
to RNA, and translation to protein. The `SeqRecord` wraps a `Seq`
together with metadata such as an identifier and description.

Docs: https://biopython.org/docs/latest/Tutorial/
"""
from IPython.core.display import display, HTML

# Biopython imports for this example.
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

# A short stretch of DNA, the start of a fictional gene.
dna = Seq("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG")

heading("1. A DNA sequence and its operations")
note(f"Original DNA (5'->3'): <code>{dna}</code> &mdash; length {len(dna)} bases.")

# Like strings, you can index, slice, and count.
note(f"First codon: <code>{dna[0:3]}</code>. GC count: {dna.count('G') + dna.count('C')}.")

# Biology-aware operations.
note(f"Complement: <code>{dna.complement()}</code>")
note(f"Reverse complement: <code>{dna.reverse_complement()}</code>")
note(f"Transcribed to mRNA: <code>{dna.transcribe()}</code>")

# Translate to protein. The * character marks a stop codon.
protein = dna.translate(to_stop=False)
note(f"Translated protein: <code>{protein}</code>")

heading("2. Wrapping a sequence in a SeqRecord")
note(
    "A SeqRecord adds identity and annotation around a Seq, which is "
    "what tools like SeqIO read and write."
)

record = SeqRecord(
    dna,
    id="GENE001",
    name="hypothetical_gene",
    description="A short example DNA sequence for demonstration",
)

display(HTML(
    f"<pre>id:          {record.id}\n"
    f"name:        {record.name}\n"
    f"description: {record.description}\n"
    f"sequence:    {record.seq}\n"
    f"length:      {len(record)} bp</pre>"
), append=True)
