# ---------------------------------------------------------------------
# Aligning two protein sequences with PairwiseAligner.
# ---------------------------------------------------------------------

from Bio import Align
from Bio.Align import substitution_matrices

heading("Pairwise alignment with Bio.Align")
note(
    "`PairwiseAligner` is Biopython's modern interface for sequence "
    "alignment. You configure the mode (global or local), scoring, "
    "and gap penalties, then call `aligner.align(seq1, seq2)`."
)

# Two short, related protein fragments. Imagine these are homologous
# regions from two species' versions of the same enzyme.
protein_a = "MEEPQSDPSVEPPLSQETFSDLWKLLPENN"
protein_b = "MEEPQSDLSIEPPLSQETFSELWKLLPPNN"

aligner = Align.PairwiseAligner()
aligner.mode = "global"  # Needleman-Wunsch end-to-end alignment.
aligner.substitution_matrix = substitution_matrices.load("BLOSUM62")
aligner.open_gap_score = -10
aligner.extend_gap_score = -1

alignments = aligner.align(protein_a, protein_b)
best = alignments[0]

note(f"Best alignment score: <strong>{best.score:.1f}</strong>")
note("The aligner returns alignments lazily; index 0 is the top-scoring one.")

# The string form of an Alignment shows the two rows with a match line
# between them.
display(HTML(f"<pre>{best}</pre>"), append=True)

heading("Switching to local alignment")
note(
    "Local alignment (Smith-Waterman) finds the best matching "
    "sub-region rather than aligning end-to-end. Useful when only "
    "part of two sequences is expected to be homologous."
)

# Embed a conserved motif inside otherwise unrelated flanking sequence.
seq_x = "AAAAAAAAGGTACGTACGTAATTTTTTTT"
seq_y = "CCCCCGGTACGTACGTAACCCCC"

local_aligner = Align.PairwiseAligner()
local_aligner.mode = "local"
local_aligner.match_score = 2
local_aligner.mismatch_score = -1
local_aligner.open_gap_score = -2
local_aligner.extend_gap_score = -0.5

local_best = local_aligner.align(seq_x, seq_y)[0]
note(f"Local alignment score: <strong>{local_best.score:.1f}</strong>")
display(HTML(f"<pre>{local_best}</pre>"), append=True)

# Alignment objects expose the aligned coordinate blocks, useful for
# downstream analysis.
note("Aligned coordinate blocks (start, end) on each sequence:")
display(HTML(f"<pre>{local_best.aligned}</pre>"), append=True)
