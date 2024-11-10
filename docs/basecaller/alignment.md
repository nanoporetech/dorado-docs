# Alignment

Dorado uses the [minimap2 aligner]({{mm2_docs}}) to align basecalled sequences to
a reference and supports aligning existing basecalls or producing aligned output directly.

## Aligning existing basecalls

To align existing basecalls, run:

```dorado
dorado aligner <index> <calls> > aligned.bam
```

where index is a reference to align to in (FASTQ/FASTA/.mmi) format and reads is a
folder or file in any HTS format.

### Writing to an output directory

When reading from an input folder, `dorado aligner` also supports writing aligned files
to an output directory, which will preserve the file structure of the inputs:

```dorado
dorado aligner <index> <calls-dir> --output-dir <output-dir>
```

### Alignment summary

An alignment summary containing alignment statistics for each read can be generated
with the `--emit-summary` argument.

!!! note

    The `--emit-summary` argument requires that the `--output-dir <output-dir>` argument is set.

    The alignment summary file will be written into `<output-dir>`.

## Alignment during basecalling

Including alignment during basecalling should not have a significant impact on overall basecalling throughput.
Although alignment is a CPU intensive operation, basecalling throughput is generally limited
by the GPU while the CPU is under-utilised. Dorado can make efficient use of both the
GPU for basecalling and the otherwise under-utilised CPU for alignment, performing both
concurrently.

To basecall with alignment with `dorado basecaller` or `dorado duplex`, add the `--reference` argument:

```dorado
dorado basecaller <model> <reads> --reference <index> > aligned.bam
dorado duplex     <model> <reads> --reference <index> > aligned.bam
```

## Minimap2 options

Alignment uses `minimap2` and by default uses the `lr:hq` preset.
This can be overridden by passing a minimap option string, `--mm2-opts`,
using the '-x ' option and/or individual options such as -k and -w to set kmer and
window size respectively.

```dorado
dorado aligner <index> <calls> --output-dir <output-dir> --mm2-opts "-x splice --junc-bed <annotations_file>"
dorado aligner <index> <calls> --output-dir <output-dir> --mm2-opts --help

dorado basecaller <model> <reads> --reference <index> --mm2-opts "-k 15 -w 10" > aligned.bam
```

For a complete list of supported minimap2 options use '--mm2-opts "--help"'. For example:

```dorado hl_lines="1"
$ dorado aligner <index> <calls> --mm2-opts "--help"

Optional arguments:
  -h, --help   shows help message and exits
  -k           minimap2 k-mer size for alignment (maximum 28).
  -w           minimap2 minimizer window size for alignment.
  -I           minimap2 index batch size.
  --secondary  minimap2 outputs secondary alignments
  -N           minimap2 retains at most INT secondary alignments
  -Y           minimap2 uses soft clipping for supplementary alignments
  -r           minimap2 chaining/alignment bandwidth and optionally long-join bandwidth specified as NUM,[NUM]
  --junc-bed   Optional file with gene annotations in the BED12 format (aka 12-column BED), or intron positions in 5-column BED. With this option, minimap2 prefers splicing in annotations.
  -x           minimap2 preset for indexing and mapping. [default: "lr:hq"]
```

!!! warning

    Not all arguments from `minimap2` are currently available and parameter names are not finalized and may change.

## Counting overlaps

The `--bed-file <bed>` argument is available in the `dorado basecaller` and `dorado aligner`.
This argument specifies a `.bed` filepath which is used to count the number of overlaps between
the bed file regions and the alignments generated.

This number is written to the BAM file output as the `bh` read tag.
