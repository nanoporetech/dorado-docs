# Barcode Classification

Dorado supports barcode classification for existing basecalls as well as producing barcode classified
basecalls directly.

The default heuristic for double-ended barcodes is to look for them on **either** end of the read.
This results in a higher classification rate but can also result in a higher false positive count.
To address this, Dorado `basecaller` also provides a `--barcode-both-ends` option to force
double-ended barcodes to be detected on both ends before classification.
This will reduce false positives dramatically, but also lower overall classification rates.

## In-line with basecalling

In this mode, reads are classified into their barcode groups **during** basecalling as part of
the same command. To enable this, run:

```dorado
dorado basecaller <model> <reads> --kit-name <barcode-kit-name> > calls.bam
```

This will result in a single output stream with classified reads. The classification will be
reflected in the read group name as well as in the `BC` tag of the output record.

The output from Dorado `basecaller` can then be demultiplexed into per-barcode BAMs using Dorado `demux`.

If the barcoded reads are already classified when in-line barcoding, ensure the
`--no-classify` argument is set, otherwise demux will search for barcodes again
causing issues if reads are [trimmed]({{find("read_trimming")}}).

```dorado
dorado demux --output-dir <output-dir> --no-classify <input-bam>
```

This will output a BAM file per barcode in the `output-dir`.

As the barcode information is also stored in the BAM `RG` header, demultiplexing is possible
using `samtools split`.

```bash
samtools split -u <output-dir>/unclassified.bam -f "<output-dir>/<prefix>_%!.bam" <input-bam>
```

However, `samtools split` uses the full `RG` string as the filename suffix, which can result in very long
file names. We recommend using Dorado `demux` to split barcoded BAMs.

## Classifying existing datasets

!!! warning

    Ensure `--no-trim` was set during basecalling otherwise duplex will fail to classify reads as they
    have had their barcodes removed.

Existing basecalled datasets **which have not been trimmed** can be classified and demultiplexed
into per-barcode BAMs using the `demux` subcommand.

```dorado
dorado demux --kit-name <kit-name> --output-dir <output-dir-for-demuxed-bams> <reads>
```

`<reads>` can either be a folder or a single file in an HTS format (e.g. FASTQ, BAM, etc.) or a
 stream of an HTS format (e.g. the output of Dorado `basecaller`).

```dorado
dorado basecaller <model> <reads> --no-trim ... | dorado demux --kit-name <kit-name> --output-dir <output-dir> ...
```

This results in multiple BAM files being generated in the output folder, one per barcode
(formatted as `KITNAME_BARCODEXX.bam`) and one for all unclassified reads.
As with the in-line mode, `--no-trim` and `--barcode-both-ends` are also available as additional options.

If the input file is aligned/sorted and `--no-trim` is chosen, each of the output barcode-specific
BAM files will also be sorted and indexed. However, if trimming is enabled (which is the default),
the alignment information is removed and the output BAMs are unaligned. This is done because the
alignment tags and positions are invalidated once a sequence is altered.

Here is an example output folder

```bash
$ dorado demux --kit-name SQK-RPB004 --output-dir /tmp/demux reads.fastq

$ ls -1 /tmp/demux
SQK-RPB004_barcode01.bam
SQK-RPB004_barcode02.bam
SQK-RPB004_barcode03.bam
...
unclassified.bam
```

A summary file listing each read and its classified barcode can be generated with the
`--emit-summary` option in Dorado `demux`. The file will be saved in the `--output-dir` folder.

## Demultiplexing mapped reads

If the input data files contain mapping data, this information can be preserved in the output files.
To do this, you must use the `--no-trim` option. Trimming the barcodes will invalidate any mapping
information that may be contained in the input files, and therefore the application will exclude
any mapping information if `--no-trim` is not specified.

It is also possible to get Dorado `demux` to sort and index any output bam files that contain
mapped reads. To enable this, use the `--sort-bam` option. If you use this option then you must
also use the `--no-trim` option, as trimming will prevent any mapping information from being
included in the output files. Index files (.bai extension) will only be created for BAM files
that contain mapped reads and were sorted. Note that for large datasets sorting the output
files may take a few minutes.

### Using a sample sheet

Dorado is able to use a sample sheet to restrict the barcode classifications to only those
present, and to apply aliases to the detected classifications. This is enabled by passing
the path to a sample sheet to the `--sample-sheet` argument when using the `basecaller` or
`demux` commands. See [here]({{find("sample_sheet")}}) for more information.

### Custom barcodes

In addition to supporting the standard barcode kits from Oxford Nanopore, Dorado also supports
specifying custom barcode kit arrangements and sequences. This is done by passing a barcode
arrangement file via the `--barcode-arrangement` argument (either to Dorado `demux` or
Dorado `basecaller`). Custom barcode sequences can optionally be specified via the
`--barcode-sequences` option. See [here]({{find("custom_barcode")}}) for more details.

## CLI reference

Here's a slightly re-formatted output from the Dorado `demux` subcommand for reference.

!!! info

    Please check the `--help` output of your own installation of dorado as this page may be outdated
    and argument defaults have been omitted as they are platform specific.

```text hl_lines="1"

❯ dorado demux --help

Positional arguments:
  reads                  An input file or the folder containing input file(s) (any HTS format).

Optional arguments:
  -h, --help             shows help message and exits
  -v, --verbose          [may be repeated]
  -t, --threads          Combined number of threads for barcoding and output generation.
                            Default uses all available threads.

Input data arguments:
  -r, --recursive        If the 'reads' positional argument is a folder any subfolders will also be
                            searched for input files.
  -l, --read-ids         A file with a newline-delimited list of reads to demux.
  -n, --max-reads        Maximum number of reads to process. Process all reads by default.

Output arguments:
  -o, --output-dir       Output folder for demultiplexed reads. [required]
  --emit-fastq           Output in fastq format. Default is BAM.
  --emit-summary         If specified, a summary file containing the details of the primary alignments
                            for each read will be emitted to the root of the output folder.
  --sort-bam             Sort any BAM output files that contain mapped reads.
                            Using this option requires that the --no-trim option is also set.

Classification arguments:
  --kit-name             Barcoding kit name. Cannot be used with --no-classify.
  --sample-sheet         Path to the sample sheet to use.
  --barcode-both-ends    Require both ends of a read to be barcoded for a double ended barcode.
  --barcode-arrangement  Path to file with custom barcode arrangement.
  --barcode-sequences    Path to file with custom barcode sequences.
  --no-classify          Skip barcode classification. Only demux based on existing classification in reads.
                            Cannot be used with --kit-name or --sample-sheet.

Trimming arguments:
  --no-trim              Skip barcode trimming. If this option is not chosen, trimming is enabled.
                            Note that you should use this option if your input data is mapped and
                            you want to preserve the mapping in the output files, as trimming will
                            result in any mapping information from the input file(s) being discarded.
```
