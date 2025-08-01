---
samtools: https://www.htslib.org/doc/samtools-view.html
bgzip: https://www.htslib.org/doc/bgzip.html
hifiasm: https://github.com/chhylp123/hifiasm
flye: https://github.com/mikolmogorov/Flye
medaka: https://github.com/nanoporetech/medaka
NCMtalk: https://youtu.be/IB6DmU40NIU?t=377
---


# Dorado Variant

!!! example "Alpha Release"

    Dorado `variant` is an early-stage diploid small variant caller, it is released for experimental and evaluation purposes.

    This version is intended for feedback and should not yet be considered production-ready.

## Should I use `variant` or `polish`?

Dorado variant is a short variant caller for diploid samples aligned to a haploid species reference (e.g. GRCh38) whereas `polish` is intended for workflows involving reads aligned to a haplotype-resolved (or haploid) draft assembly.

Although Dorado `polish` can also generate a VCF file of variants, there are some substantial distinctions between the two tools.

| `dorado polish`      | `dorado variant`             |
| -------------------- | -------------------- |
| - Polishing of draft assemblies<br>- Input is a haplotype-resolved draft assembly<br>- Output is a polished sequence<br>- Optionally, a VCF/gVCF of diffs is output<br>- Uses specialised polishing models| - Diploid variant calling<br>- Input is a reference genome<br>- Output is a VCF/gVCF of called diploid variants<br>- Uses specialised variant calling models|

## Quick Start

```dorado
# Align the reads using dorado aligner, sort and index
dorado aligner <ref.fasta> <reads.bam> | samtools sort --threads <num_threads> > aligned_reads.bam
samtools index aligned_reads.bam

# Call variants
dorado variant <aligned_reads.bam> <ref.fasta> > variants.vcf
```

For this preview release, current models require signal-level information encoded in the move tables in the input BAM file. This requires the `--emit-moves` flag to be set during basecalling.

In case the input basecalled reads are in a FASTQ format with the HTS-style ONT tags, please use the `--add-fastq-rg` option with Dorado `aligner` to ensure proper header formatting:
```dorado
# Align the reads using dorado aligner, sort and index
dorado aligner --add-fastq-rg <ref.fasta> <reads.fastq> | samtools sort --threads <num_threads> > aligned_reads.bam
samtools index aligned_reads.bam
```

### Output to a folder

```dorado
dorado variant <aligned_reads> <reference> -o <output_dir>
```

Specifying `-o` will write the output to one or more files stored in the given output directory (and create the directory if it doesn't exist). Concretely:

- VCF file: `<output_dir>/variants.vcf` which contains only variant calls by default, or records for all positions if `--gvcf` is specified.

## Resources

Dorado `variant` will automatically select the compute resources to perform variant calling. It can use one or more GPU devices. Variant calling can be performed on CPU-only, but we highly recommend to run on GPU for desired performance. High-memory GPUs are recommended to run this tool.

To specify resources manually use:

- `-x / --device` - to specify specific GPU resources (if available).
- `--threads` - to set the maximum number of threads to be used for everything but the inference.
- `--infer-threads` - number of inference workers to use (per device). For CPU-only runs, this specifies the number of CPU inference threads.
- `--batchsize` - batch size for inference, important to control memory usage on the GPUs.

Example:

```dorado
dorado variant aligned_reads.bam reference.fasta --device cuda:0 --threads 24 > variants.vcf
```

## Models

By default, `variant` queries the BAM and selects the best model for the basecalled reads, if supported.

Alternatively, a model can be selected through the command line in the following way:

```dorado
dorado variant --model <value> ...
```

| Value    | Description |
| -------- | ------- |
| `auto`  | Determine the best compatible model based on input data. |
| `<basecaller_model>` | Simplex basecaller model name (e.g. `dna_r10.4.1_e8.2_400bps_hac@v5.0.0`) |
| `<variant_model>` | Variant calling model name (e.g. `dna_r10.4.1_e8.2_400bps_hac@v5.0.0_variant_mv@v1.0`) |
| `<path>` | Local path on disk where the model can be loaded from. |

When the `auto` or the `<basecaller_model>` syntax is used the most recent version of a compatible model will be selected for variant calling.

Current variant calling models require the presence of move tables in the input BAM file. Move tables need to be exported during basecalling.

If a non-compatible model is selected for the input data, or if there are multiple read groups in the input dataset which were generated using different basecaller models, Dorado `variant` will report an error and stop execution.

### Supported basecaller models

- `dna_r10.4.1_e8.2_400bps_hac@v5.0.0`

More models will be supported in the near future. This is an alpha release.

## Common questions and Troubleshooting

### I created a merged BAM file composed of multiple different data types. Why can't I call variants on this dataset? Using `--ignore-read-groups` does not help either.

Please see the following section in Dorado `polish`:
[I created a merged BAM file composed of multiple different data types]({{find("polish")}}#i-created-a-merged-bam-file-composed-of-multiple-different-data-types-why-cant-i-polish-it-using-ignore-read-groups-does-not-help-either)

### Memory consumption / Torch out-of-memory (OOM) issues

The default inference batch size (`10`) may be too high for your GPU. If you are experiencing warnings/errors regarding available GPU memory, try reducing the batch size:

```dorado
dorado variant aligned_reads.bam reference.fasta --batchsize <number> > variants.vcf
```

or the number of inference workers (the default is `2` workers per device):

```dorado
dorado variant aligned_reads.bam reference.fasta --infer-threads 1 > variants.vcf
```

Note that the GPU memory consumption also depends on the coverage of the input data, as feature tensor size varies relative to this.

### "[error] Input BAM file was not aligned using Dorado."

Dorado `variant` accepts only BAMs aligned with Dorado `aligner`. Aligners other than Dorado `aligner` are not supported.

Example usage:
```dorado
dorado aligner <draft.fasta> <reads.bam> | samtools sort --threads <num_threads> > aln.bam
samtools index aln.bam
```

### "[error] Input BAM file has no basecaller models listed in the header."

Please refer to this [section]({{find("polish")}}#error-input-bam-file-has-no-basecaller-models-listed-in-the-header).

### "[error] Duplex basecalling models are not supported."

Dorado `variant` currently supports data generated using only the simplex basecallers.

### Does Dorado Variant phase variants?

At this early stage, Dorado `variant` does not yet produce phased VCF variants. This is work in progress.
