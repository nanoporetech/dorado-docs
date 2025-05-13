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

Additionally, `dorado polish` can output a VCF file containing records for all variants discovered during polishing, or a gVCF file containing records for all locations in the input draft sequences.

## Quick Start

### Consensus
```bash
# Align the reads using dorado aligner, sort and index
dorado aligner <draft.fasta> <reads.bam> | samtools sort --threads <num_threads> > aligned_reads.bam
samtools index aligned_reads.bam

# Call consensus
dorado polish <aligned_reads.bam> <draft.fasta> > polished_assembly.fasta
```

In the above example, `<aligned_reads>` is a BAM of reads aligned to a draft by `dorado aligner` and `<draft>` is a FASTA or FASTQ file containing the draft assembly. The draft can be uncompressed or compressed with `bgzip`.

### Consensus on bacterial genomes
```dorado
dorado polish <aligned_reads> <draft> --bacteria > polished_assembly.fasta
```

This will automatically resolve a suitable bacterial polishing model, if one exits for the input data type.

### Variant calling
```bash
dorado polish <aligned_reads> <draft> --vcf > polished_assembly.vcf
dorado polish <aligned_reads> <draft> --gvcf > polished_assembly.all.vcf
```

Specifying the `--vcf` or `--gvcf` flags will output a VCF file to stdout instead of the consensus sequences.

### Output to a folder
```dorado
dorado polish <aligned_reads> <draft> -o <output_dir>
```

Specifying the `-o` will write multiple files to a given output directory (and create the directory if it doesn't exist):
- Consensus file: `<output_dir>/consensus.fasta` by default, or `<output_dir>/consensus.fastq` if `--qualities` is specified.
- VCF file: `<output_dir>/variants.vcf` which contains only variant calls by default, or records for all positions if `--gvcf` is specified.

## Resources

Dorado `polish` will automatically select the compute resources to perform polishing. It can use one or more GPU devices, or the CPU, to call consensus.

To specify resources manually use:
- `-x / --device` - to specify specific GPU resources (if available). For more information see here.
- `--threads` -  to set the maximum number of threads to be used for everything but the inference.
- `--infer-threads` -  to set the number of CPU threads for inference (when "--device cpu" is used).
- `--batchsize` - batch size for inference, important to control memory usage on the GPUs.

Example:
```dorado
dorado polish reads_to_draft.bam draft.fasta --device cuda:0 --threads 24 > consensus.fasta
```

## Models

By default, `polish` queries the BAM and selects the best model for the basecalled reads, if supported.

Alternatively, a model can be selected through the command line using the `--model` argument with the following values:

| Value    | Description |
| -------- | ------- |
| `auto`  | Determine the best compatible model based on input data. |
| `<basecaller_model>` | Simplex basecaller model name (e.g. `dna_r10.4.1_e8.2_400bps_sup@v5.0.0`) |
| `<polishing_model>` | Polishing model name (e.g. `dna_r10.4.1_e8.2_400bps_sup@v5.0.0_polish_rl_mv`) |
| `<path>` | Local path on disk where the model will be loaded from. |

When `auto` or `<basecaller_model>` syntax is used and the input is a v5.0.0 dataset, the data will be queried for the presence move tables and an best polishing model selected for the data. Move tables need to be exported during basecalling. If available, this allows for higher polishing accuracy.

If a non-compatible model is selected for the input data, or there are multiple read groups in the input dataset which were generated using different basecaller models, `dorado polish` will report an error and stop execution.

### Supported basecaller models
- `dna_r10.4.1_e8.2_400bps_sup@v5.0.0`
- `dna_r10.4.1_e8.2_400bps_hac@v5.0.0`
- `dna_r10.4.1_e8.2_400bps_sup@v4.3.0`
- `dna_r10.4.1_e8.2_400bps_hac@v4.3.0`
- `dna_r10.4.1_e8.2_400bps_sup@v4.2.0`
- `dna_r10.4.1_e8.2_400bps_hac@v4.2.0`


### Move Table Aware Models

Significantly more accurate assemblies can be produced by giving the polishing model access to additional information about the underlying signal for each read. For more information, see this section from the [NCM 2024](https://youtu.be/IB6DmU40NIU?t=377) secondary analysis update.

Dorado `polish` includes models which can use the move table to get temporal information about each read. These models will be selected automatically if the corresponding `mv` tag is in the input BAM. To do this, pass the `--emit-moves` tag to `dorado basecaller` when basecalling. To check if a BAM contains the move table for reads, use samtools:
```bash
samtools view --keep-tag "mv" -c <reads_to_draft_bam>
```

The output should be equal to the total number of reads in the bam (`samtools view -c <reads_to_draft_bam>`).

If move tables are not available in the BAM, then the non-move table-aware model will be automatically selected.

## FAQ

### How is Dorado `polish` different from Medaka?

[Medaka]({{medaka}}) and Dorado `polish` are both assembly polishing tools. They accept the same input formats and produce the same output formats, and in principle they could run the same polishing model to produce equivalent results. However, Dorado `polish` is optimised for higher performance, and can support more accurate models with more computationally intensive architectures. For use cases in low-resource settings (small genomes such as bacteria with CPUs only available) Medaka remains the recommended tool. For large genomes or in other instances where speed is important, we suggest trying Dorado `polish`.

### Should I use `correct` or `polish`?

Dorado `polish` is a post-assembly tool and it is intended to improve the accuracy of pre-existing
assemblies. Dorado `correct` conversely is a pre-assembly tool and is intended to improve the
contiguity of an assembly by improving the fidelity of reads used to create it.

### "How do I go from raw POD5 data to a polished T2T assembly?"

Here is a high-level example workflow:
```dorado
# Generate basecalled data with dorado basecaller
dorado basecaller <model> pod5s/ --emit-moves > calls.bam
samtools fastq calls.bam > calls.fastq

# Apply dorado correct to a set of reads that can be used as input in an assembly program.
dorado correct calls.fastq > corrected.fastq

# Assemble the genome using those corrected reads
<some_assembler> --input corrected.fastq > draft_assembly.fasta

# Align original calls to the draft assembly
dorado aligner calls.bam draft_assembly.fasta > aligned_calls.bam

# Run dorado polish using the raw reads aligned to the draft assembly
dorado polish aligned_calls.bam draft_assembly.fasta > polished_assembly.fasta
```

## Troubleshooting

### GPU Memory Issues

The default inference batch size (`16`) may be too high for your GPU.
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

Note that using multiple CPU inference threads can cause much higher memory usage.

### "[error] Caught exception: Could not open index for BAM file: 'aln.bam'!"
Example message:
```dorado
$ dorado polish aln.bam assembly.fasta > polished.fasta
[2024-12-23 07:18:23.978] [info] Running: "polish" "aln.bam" "assembly.fasta"
[E::idx_find_and_load] Could not retrieve index file for 'aln.bam'
[2024-12-23 07:18:23.987] [error] Caught exception: Could not open index for BAM file: 'aln.bam'!
```

This message means that there the input BAM file does not have an accompanying index file `.bai`. This may also mean that the input BAM file is not sorted, which is a prerequisite for producing the `.bai` index using `samtools`.

`dorado polish` requires input alignments to be produced using `dorado aligner`. When `dorado aligner` outputs alignments to `stdout`, they are not sorted automatically. Instead, `samtools` needs to be used to sort and index the BAM file. For example:
```dorado
dorado aligner <draft.fasta> <reads.bam> | samtools sort --threads <num_threads> > aln.bam
samtools index aln.bam
```
Note that the sorting step is added after the pipe symbol.

The output from dorado aligner is already sorted when the output is to a folder, specified using the `--output-dir` option.
```dorado
dorado aligner --output-dir <out_dir> <draft.fasta> <reads.bam>
```

### "[error] Caught exception: Input BAM file has no basecaller models listed in the header."

`dorado polish` requires that the aligned BAM has one or more `@RG` lines in the header. Each `@RG` line needs to contain a basecaller model used for generating the reads in this group. This information is required to determine the compatibility of the selected polishing model, as well as for auto-resolving the model from data.

When using `dorado aligner` please provide the input basecalled reads in the BAM format. The basecalled reads BAM file (`e.g. calls.bam`) contains the `@RG` header lines, and this will be propagated into the aligned BAM file.

However, if input reads are given in the `FASTQ`, the output aligned BAM file will _not_ contain `@RG` lines, and it will not be possible to use it for polishing.

Note that, even if the input FASTQ file has header lines in the form of:
```
@74960cfd-0b82-43ed-ae04-05162e3c0a5a qs:f:27.7534 du:f:75.1604 ns:i:375802 ts:i:1858 mx:i:1 ch:i:295 st:Z:2024-08-29T22:06:03.400+00:00 rn:i:585 fn:Z:FBA17175_7da7e070_f8e851a5_5.pod5 sm:f:414.101 sd:f:107.157 sv:Z:pa dx:i:0 RG:Z:f8e851a5d56475e9ecaa43496da18fad316883d8_dna_r10.4.1_e8.2_400bps_sup@v5.0.0
```
`dorado aligner` will not automatically add the `@RG` header lines. BAM input needs to be used for now.

TL;DR:
- Use reads in BAM format (not FASTQ) as input for alignment:
```dorado
dorado aligner draft.fasta calls.bam
```

### "[error] Caught exception: Input BAM file was not aligned using Dorado."

`dorado polish` accepts only BAMs aligned with `dorado aligner`. Aligners other than `dorado aligner` are not supported.

Example usage:
```dorado
dorado aligner <draft.fasta> <reads.bam> | samtools sort --threads <num_threads> > aln.bam
samtools index aln.bam
```

### "[error] Caught exception: The input BAM contains more than one read group. Please specify --RG to select which read group to process."

It is possible that the input BAM file contains more than 1 read group. In this case, `dorado polish` requires that a single read group is selected for processing using the `--RG <id>` command line argument. The `<id>` should exactly match the `ID:` field in one of the `@RG` lines in the input BAM/SAM file.

Specifying the `--RG` option will filter out any read which does not belong to that read group and will apply the appropriate polishing model for that read group based on the basecaller model specified in the corresponding `@RG` line in the input BAM file.

Specifying a read group which corresponds to duplex data will not work because `dorado polish` currently does not have duplex polishing models available.

In case of a duplex BAM - note that by default the simplex parents of the duplex reads will also be present in the output BAM file from Dorado. Consider filtering these out first if this could bias your results.
