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

!!! tip inline end "Should I use `variant` or `polish`?"

    [See here]({{find("variant")}}#should-i-use-variant-or-polish)

Dorado `polish` is a high accuracy assembly polishing tool which outperforms
similar tools for most ONT-based assemblies.

It takes as input a draft assembly produced by a tool such as [Hifiasm](https://github.com/chhylp123/hifiasm) or [Flye](https://github.com/mikolmogorov/Flye) and aligned reads, and outputs an updated version of the assembly.

Additionally, Dorado `polish` can output a VCF file containing records for all variants discovered during polishing, or a gVCF file containing records for all locations in the input draft sequences.

Note that Dorado `polish` is a **haploid** polishing tool and does _not_ implement any sort of phasing internally. It will take input alignment data _as is_ and run it through the polishing model to produce the consensus sequences. For more information, please take a look at [this section](#polishing-diploidpolyploid-assemblies).

## Quick Start

### Consensus

```dorado
# Align unmapped reads to a reference using dorado aligner, sort and index
dorado aligner <draft.fasta> <unmapped_reads.bam> | samtools sort --threads <num_threads> > aligned_reads.bam
samtools index aligned_reads.bam

# Call consensus
dorado polish <aligned_reads.bam> <draft.fasta> > polished_assembly.fasta
```

In the above example, `<aligned_reads>` is a BAM of reads aligned to a draft by Dorado `aligner` and `<draft>` is a FASTA or FASTQ file containing the draft assembly. The draft can be uncompressed or compressed with `bgzip`.

### Consensus from a FASTQ input instead of BAM

In case a FASTQ file was produced during basecalling instead of a BAM file, you will need to provide a flag `--add-fastq-rg` to Dorado `aligner` to have it generate the proper BAM header required for Dorado `polish`.

Note that this may take some time to run because it requires an extra pass over the input data prior to alignment.

This feature supports only FASTQ files with HTS-style tags in the header and will not work for the old MinKnow style FASTQ files.

Here is a full example:
```dorado
# Align reads to a reference using dorado aligner, sort and index
dorado aligner --add-fastq-rg <draft.fasta> <reads.fastq> | samtools sort --threads <num_threads> > aligned_reads.bam
samtools index aligned_reads.bam

# Call consensus
dorado polish <aligned_reads.bam> <draft.fasta> > polished_assembly.fasta
```

### Consensus on bacterial genomes

```dorado
dorado polish <aligned_reads> <draft> --bacteria > polished_assembly.fasta
```

This will automatically resolve a suitable bacterial polishing model, if one exits for the input data type.

### Variant calling

```dorado
dorado polish <aligned_reads> <draft> --vcf > polished_assembly.vcf
dorado polish <aligned_reads> <draft> --gvcf > polished_assembly.all.vcf
```

Specifying `--vcf` or `--gvcf` flags will output a VCF file to stdout instead of the consensus sequences.

### Output to a folder
```dorado
dorado polish <aligned_reads> <draft> -o <output_dir>
```

Specifying `-o` will write multiple files to a given output directory (and create the directory if it doesn't exist):

- Consensus file: `<output_dir>/consensus.fasta` by default, or `<output_dir>/consensus.fastq` if `--qualities` is specified.
- VCF file: `<output_dir>/variants.vcf` which contains only variant calls by default, or records for all positions if `--gvcf` is specified.

## Resources

Dorado `polish` will automatically select the compute resources to perform polishing. It can use one or more GPU devices, or the CPU, to call consensus.

To specify resources manually use:

- `-x / --device` - to specify specific GPU resources (if available).
- `--threads` -  to set the maximum number of threads to be used for everything but the inference.
- `--infer-threads` -  to set the number of CPU threads for inference (when "--device cpu" is used).
- `--batchsize` - batch size for inference, important to control memory usage on the GPUs.

Example:

```dorado
dorado polish reads_to_draft.bam draft.fasta --device cuda:0 --threads 24 > consensus.fasta
```

## Models

Dorado `polish` auto-resolves the polishing model based on the input BAM file. The BAM file needs to contain the `@RG` headers with the basecaller model name specified, otherwise the model will not be resolved. If the input BAM records contain move tables, an appropriate move-aware polishing model will be selected.

Once the model is resolved, Dorado `polish` will either download it or look it up in the models-directory if specified.

For example:
```dorado
dorado polish reads_to_draft.bam draft.fasta > consensus.fasta
```
will find the compatible model based on the input BAM file and download it to a temporary folder.

When `--models-directory` is specified, the resolved polishing model will first be looked up in the models-directory, and only downloaded if the model does not exist. The specified models-directory must exist. Example:
```dorado
mkdir -p models
dorado polish --models-directory models reads_to_draft.bam draft.fasta > consensus.fasta
```

More information about the `--models-directory` can be found in [this section](#model-search-directory-and-temporary-model-downloads)

If there are multiple read groups in the input dataset which were generated using different basecaller models, Dorado `polish` will report an error and stop execution.

### Move Table Aware Models

Significantly more accurate assemblies can be produced by giving the polishing model access to additional information about the underlying signal for each read. For more information, see this section from the [NCM 2024](https://youtu.be/IB6DmU40NIU?t=377) secondary analysis update.

Dorado `polish` includes models which can use the move table to get temporal information about each read. These models will be selected automatically if the corresponding `mv` tag is in the input BAM. To do this, pass the `--emit-moves` tag to Dorado `basecaller` when basecalling. To check if a BAM contains the move table for reads, use samtools:
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

### How do I go from raw POD5 data to a polished T2T assembly?

Here is a high-level example workflow:
```dorado
# Generate basecalled data with dorado basecaller
dorado basecaller <model> pod5s/ --emit-moves > calls.bam
samtools fastq calls.bam > calls.fastq

# Apply dorado correct to a set of reads that can be used as input in an assembly program.
dorado correct calls.fastq > corrected.fasta

# Assemble the genome using those corrected reads
<some_assembler> --input corrected.fasta > draft_assembly.fasta

# Align original calls to the draft assembly
dorado aligner draft_assembly.fasta calls.bam > aligned_calls.bam

# Run dorado polish using the raw reads aligned to the draft assembly
dorado polish aligned_calls.bam draft_assembly.fasta > polished_assembly.fasta
```

### Polishing diploid/polyploid assemblies

Dorado `polish` is a **haploid** polishing tool and does _not_ implement any sort of phasing internally. It will take input alignment data _as is_ and run it through the polishing model to produce the consensus sequences.

In order to polish diploid/polyploid assemblies, it is up to the user to properly separate haplotypes before giving the data to Dorado `polish`.

We are currently working on a set of best practices. In the meantime, an unofficially suggested approach to polish diploid genomes would be to align the reads using the  `lr:hqae` [Minimap2 setting](https://github.com/lh3/minimap2/releases/tag/v2.28) as this was specifically designed for alignment back to a diploid genome. This setting is available through Dorado `aligner` using the following option:
```dorado
dorado aligner --mm2-opts "-x lr:hqae" <ref> <reads>
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

### "[error] Could not open index for BAM file: 'aln.bam'!"
Example message:
```dorado
$ dorado polish aln.bam assembly.fasta > polished.fasta
[2024-12-23 07:18:23.978] [info] Running: "polish" "aln.bam" "assembly.fasta"
[E::idx_find_and_load] Could not retrieve index file for 'aln.bam'
[2024-12-23 07:18:23.987] [error] Could not open index for BAM file: 'aln.bam'!
```

This message means that there the input BAM file does not have an accompanying index file `.bai`. This may also mean that the input BAM file is not sorted, which is a prerequisite for producing the `.bai` index using `samtools`.

Dorado `polish` requires input alignments to be produced using Dorado `aligner`. When Dorado `aligner` outputs alignments to `stdout`, they are not sorted automatically. Instead, `samtools` needs to be used to sort and index the BAM file. For example:
```dorado
dorado aligner <draft.fasta> <reads.bam> | samtools sort --threads <num_threads> > aln.bam
samtools index aln.bam
```
Note that the sorting step is added after the pipe symbol.

The output from dorado aligner is already sorted when the output is to a folder, specified using the `--output-dir` option.
```dorado
dorado aligner --output-dir <out_dir> <draft.fasta> <reads.bam>
```

### "[error] Input BAM file has no basecaller models listed in the header."

Dorado `polish` requires that the aligned BAM has one or more `@RG` lines in the header. Each `@RG` line needs to contain a basecaller model used for generating the reads in this group. This information is required to determine the compatibility of the selected polishing model, as well as for auto-resolving the model from data.

When using Dorado `aligner` please provide the input basecalled reads in the BAM format. The basecalled reads BAM file (`e.g. calls.bam`) contains the `@RG` header lines, and this will be propagated into the aligned BAM file. Example:
```dorado
dorado aligner draft.fasta calls.bam | samtools sort --threads <num_threads> > aligned_reads.bam
samtools index aligned_reads.bam
```
Alternatively, Dorado `aligner` will automatically sort and index the alignments when an output directory is specified instead of `stdout`.
```dorado
dorado aligner --output-dir out draft.fasta calls.bam
```

However, if input basecalled reads are given in the **FASTQ** format, the aligned BAM file will _not_ contain `@RG` lines by default.
In this case, a flag `--add-fastq-rg` can be passed to Dorado `aligner`. Dorado `aligner` will then perform an additional pass over the input FASTQ data and collect all the read group / basecaller information and add it to the header.

Note that this feature will only work for the HTS-style FASTQ headers, such as:
```
@74960cfd-0b82-43ed-ae04-05162e3c0a5a qs:f:27.7534 du:f:75.1604 ns:i:375802 ts:i:1858 mx:i:1 ch:i:295 st:Z:2024-08-29T22:06:03.400+00:00 rn:i:585 fn:Z:FBA17175_7da7e070_f8e851a5_5.pod5 sm:f:414.101 sd:f:107.157 sv:Z:pa dx:i:0 RG:Z:f8e851a5d56475e9ecaa43496da18fad316883d8_dna_r10.4.1_e8.2_400bps_sup@v5.0.0
```

Example usage:
```dorado
dorado aligner --add-fastq-rg --output-dir out draft.fasta calls.bam
```

Dorado `polish` currently supports data generated using only the simplex basecallers.

### "[error] Input BAM file was not aligned using Dorado."

Dorado `polish` accepts only BAMs aligned with Dorado `aligner`. Aligners other than Dorado `aligner` are not supported.

Example usage:
```dorado
dorado aligner <draft.fasta> <reads.bam> | samtools sort --threads <num_threads> > aln.bam
samtools index aln.bam
```

### "[error] The input BAM contains more than one read group. Please specify --RG to select which read group to process."

It is possible that the input BAM file contains more than 1 read group. In this case, Dorado `polish` requires that a single read group is selected for processing using the `--RG <id>` command line argument. The `<id>` should exactly match the `ID:` field in one of the `@RG` lines in the input BAM/SAM file.

Specifying the `--RG` option will filter out any read which does not belong to that read group and will apply the appropriate polishing model for that read group based on the basecaller model specified in the corresponding `@RG` line in the input BAM file.

Specifying a read group which corresponds to duplex data will not work because Dorado `polish` currently does not have duplex polishing models available.

In case of a duplex BAM - note that by default the simplex parents of the duplex reads will also be present in the output BAM file from Dorado. Consider filtering these out first if this could bias your results.

### "[error] Duplex basecalling models are not supported."

Dorado `polish` currently supports data generated using only the simplex basecallers.

### I created a merged BAM file composed of multiple different data types. Why can't I polish it? Using `--ignore-read-groups` does not help either.

In case you created a merged BAM file, one of the following scenarios is possible:

1. **There are zero read groups in the merged BAM file.** Something went wrong in the process of data preparation. There needs to be at least one read group in the BAM file which links the data to a basecaller model.
2. **The merged BAM file has only one read group.** This is the best option, and merging was performed in a way that all colliding `@RG` headers were merged too. Since there is only one read group, there is also one basecaller model for the entire merged BAM dataset.
3. **The merged BAM file has more than one read group, but only a single basecaller model.** This can occur when data originally belonged to the same read group but the colliding read groups were not merged in the process (check the `-c` option of `samtools merge`). For example, `samtools merge` will add a unique hash to the end of each read group, because the prefix of the read groups is the same (e.g. `bc8993f4557dd53bf0cbda5fd68453fea5e94485_dna_r10.4.1_e8.2_400bps_hac@v5.0.0-1C79A650` and `bc8993f4557dd53bf0cbda5fd68453fea5e94485_dna_r10.4.1_e8.2_400bps_hac@v5.0.0-6E00935B`). Alternatively, data from multiple sequencing runs were combined, but the same basecaller model was used in all cases.
    - Using `--ignore-read-groups` will run the process using all data in this case, since it was generated using a single basecaller model.
    - Alternatively, using `--RG <read_group_id>` will select only reads which belong to this specific read group, and ignore all other reads.
    - Auto model detection is possible from the BAM file in this case, since only one basecaller model was used to produce the data.
4. **The merged BAM file has more than one read group and _more than one basecaller model_.** One or more read groups were generated using one particular basecaller model, while some other read groups were generated using another particular basecaller model. (For example, combining old and new data.) Sometimes, users may attempt to combine simplex and duplex reads into the same BAM file.
    - Dorado `polish`/`variant` can use only one selected model for inference. All currently available models were trained on individual data types (data generated by a single basecaller version) and not on a mixture of data (with the exception of the bacterial methylation polishing model). Running any model on a mixture of data may produce inferior results. This is why Dorado `polish` and Dorado `variant` enforce that only a single basecaller model is present in the input.
    - In this case, not even `--ignore-read-groups` will work because there was more than one basecaller model used to produce the data in this BAM file.
    - Using `--RG <read_group_id>` will select only reads which belong to one specific read group, and ignore all other reads.
    - Using the auto model selection cannot resolve a model from a BAM file if the input BAM file contains multiple models.
    - Auto model selection in this case is only possible if `--RG` is used.
    - Duplex basecaller models are not supported by Dorado `polish` or Dorado `variant`.
