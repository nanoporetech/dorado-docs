---
samtools: https://www.htslib.org/doc/samtools-view.html
bgzip: https://www.htslib.org/doc/bgzip.html
hifiasm: https://github.com/chhylp123/hifiasm
flye: https://github.com/mikolmogorov/Flye
medaka: https://github.com/nanoporetech/medaka
NCMtalk: https://youtu.be/IB6DmU40NIU?t=377
---

# Dorado Polish

!!! tip inline end "Should I use `correct` or `polish`?"

    [See here](#should-i-use-correct-or-polish)

Dorado `polish` is a high accuracy assembly polishing tool which outperforms
similar tools for most ONT-based assemblies.

It takes as input a draft assembly produced by a tool
such as [Hifiasm]({{hifiasm}}) or
[Flye]({{flye}}) and aligned reads
and outputs an updated version of the assembly.

## Quick Start

To produce a polished assembly from a draft and reads aligned to that draft, run

```dorado
dorado polish <aligned_reads> <draft> > polished_assembly.fasta
```

where `<aligned_reads>` is a BAM of reads aligned to a draft by Dorado `aligner`
and `<draft>` is a FASTA or FASTQ file containing the draft assembly. The draft
can be uncompressed or compressed with [bgzip]({{bgzip}}).

By default, `polish` queries the BAM and selects the best model for the basecalled
reads.

!!! info IMPORTANT
    Currently, Dorado `polish` only supports `hac@v5.0` and `sup@v5.0` basecalls.

## Move Table Aware Models

Significantly more accurate assemblies can be produced by giving the polishing
model access to additional information about the underlying signal for each
read. For more information, see this section from the
[NCM 2024 secondary analysis update]({{NCMtalk}}) .

Dorado `polish` includes models which can use the [move table]({{find("move_table")}}) to get temporal
information about each read.
These models will be selected automatically if the corresponding `mv` tag is
in the input BAM. To do this, pass the `--emit-moves` tag to
`dorado basecaller` when basecalling. To check if a BAM contains the move
table for reads, use [samtools]({{samtools}}):

```bash
samtools view --keep-tag "mv" -c <reads_to_draft_bam>
```

The output should be equal to the total number of reads in the bam. This can be found using: `samtools view -c <reads_to_draft_bam>`.

If move tables are not available in the BAM, then the non-move table-aware
model will be automatically selected.

## Specifying resources

Dorado `polish` will automatically select all available compute resources
to perform polishing.

To specify resources manually use:

* `-x / --device` to specify specific GPU resources (if available). For more information
  see [here]({{find("index")}}#specifying-hardware-resources).
* `--threads` to set the maximum number of threads to be used for everything but the inference.
* `--infer-threads` to set the number of CPU threads for inference (when "--device cpu" is used).

```dorado
dorado polish reads_to_draft.bam draft.fasta --device cuda:0 --threads 64 > consensus.fasta
```

Polishing is both compute and memory intensive. It is best run using multiple threads (≥64) on a system with:

* multiple high performance CPU cores ( > 24 cores)
* a modern GPU with a large VRAM ( > 32GB)

## FAQ

### How is Dorado `polish` different from Medaka?

[Medaka]({{medaka}}) and Dorado `polish` are both assembly polishing tools. They accept the same input formats and produce the same output formats, and in principle they could run the same polishing model to produce equivalent results. However, Dorado `polish` is optimised for higher performance, and can support more accurate models with more computationally intensive architectures. For use cases in low-resource settings (small genomes such as bacteria with CPUs only available) Medaka remains the recommended tool. For large genomes or in other instances where speed is important, we suggest trying Dorado `polish`.

### Should I use `correct` or `polish`?

Dorado `polish` is a post-assembly tool and it is intended to improve the accuracy of pre-existing
assemblies. Dorado `correct` conversely is a pre-assembly tool and is intended to improve the
contiguity of an assembly by improving the fidelity of reads used to create it.

## Troubleshooting

### GPU Memory Issues

The default inference batch size (16) may be too high for your GPU.
If you are experiencing warnings/errors regarding available GPU memory,
try reducing the batch size:

```dorado
dorado polish reads_to_draft.bam draft.fasta --batchsize <number> > consensus.fasta
```

Alternatively, consider running model inference on the CPU, although this will
take longer:

```dorado
dorado polish reads_to_draft.bam draft.fasta --device "cpu" > consensus.fasta
```

## CLI reference

Below is a slightly re-formatted output from the Dorado `polish` subcommand for reference.

!!! Info

    Please check the `--help` output of your own installation of Dorado as this page may be
    outdated and argument defaults have been omitted as they are platform specific.

```bash hl_lines="1"
> dorado polish --help
Consensus tool for polishing draft assemblies

Positional arguments:
  in_aln_bam            Aligned reads in BAM format
  in_draft_fastx        Draft assembly for polishing

Optional arguments:
  -h, --help            shows help message and exits
  -t, --threads         Number of threads for processing. Default uses all available threads.
  --infer-threads       Number of threads per device.
  -x, --device          Specify CPU or GPU device: 'auto', 'cpu', 'cuda:all' or 'cuda:<device_id>[,<device_id>...]'. Specifying 'auto' will choose either 'cpu' or 'cuda:all' depending on the presence of a GPU device.
  -v, --verbose         [may be repeated]

Input/output options (detailed usage):
  -o, --out-path        Output to a file instead of stdout.
  -m, --model           Path to correction model folder.
  -q, --qualities       Output with per-base quality scores (FASTQ).

Advanced options (detailed usage):
  -b, --batchsize       Batch size for inference.
  --draft-batchsize     Approximate batch size for processing input draft sequences.
  --window-len          Window size for calling consensus.
  --window-overlap      Overlap length between windows.
  --bam-chunk           Size of draft chunks to parse from the input BAM at a time.
  --bam-subchunk        Size of regions to split the bam_chunk in to for parallel processing
  --no-fill-gaps        Do not fill gaps in consensus sequence with draft sequence.
  --fill-char           Use a designated character to fill gaps.
  --regions             Process only these regions of the input. Can be either a path to a BED file or a list of comma-separated Htslib-formatted regions (start is 1-based, end is inclusive).
  --RG                  Read group to select.
  --ignore-read-groups  Ignore read groups in bam file.
  --tag-name            Two-letter BAM tag name for filtering the alignments during feature generation
  --tag-value           Value of the tag for filtering the alignments during feature generation
  --tag-keep-missing    Keep alignments when tag is missing. If specified, overrides the same option in the model config.
  --min-mapq            Minimum mapping quality of the input alignments. If specified, overrides the same option in the model config.
  --min-depth           Sites with depth lower than this value will not be polished.
```
