# Modified Basecalling

## Introduction

A modified nucleotide base is a nucleotide in which the canonical base (ACGTU)
has undergone some chemical change. Modified nucleotide bases play crucial roles
in various biological processes, including gene expression regulation, DNA repair,
and the immune response.

Dorado supports modified basecalling and implements this as an extension to the
normal `simplex` and `duplex` basecalling subcommands. In either case it can activated with
the addition of a modified basecalling model as shown in the [usage guide](#usage) below.


### Supported modifications

The modifications listed here are **not** necessarily available for all model speeds, and / or versions.

Please check the **[Models List]({{find("list")}})** for which modifications are available.

#### DNA modifications

| Mod | Name | CHEBI |
| |  |  |
| **4mC** | N(4)-methylcytosine | [CHEBI:21839](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:21839) |
| **5mC** | 5-Methylcytosine | [CHEBI:27551](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:27551) |
| **5hmC** | 5-Hydroxymethylcytosine | [CHEBI:76792](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:76792) |
| **6mA** | 6-Methyladenine | [CHEBI:28871](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:28871) |

#### RNA modifications

| Mod | Name | CHEBI |
| |  |  |
| **inosine** | Inosine | [CHEBI:17596](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:17596) |
| **m5C** | 5-Methylcytosine | [CHEBI:27551](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:27551) |
| **m6A** | N(6)-Methyladenosine | [CHEBI:21891](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:21891) |
| **pseU** | Pseudouridine | [CHEBI:17802](https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:17802) |

### Modification context

Modified bases are modifications to one of the canonical bases (ACGTU).
For example, `6mA` is a modified base which was originally a "canonical" `A` base.

Modified base models can be described as either being "all-context" or having some specific
context known as a "motif".

All-context modified base models will predict the presence of one or more mods at all
positions of its canonical base. Motif modified base models (which are not all-context)
will only call mods at the positions of their specific motif.

For example, given the two modified base models `5mC` and `5mCG` which both predict
the presence of `5-Methylcytosine` on canonical `C` bases, the first is an all-context
`C` model and the second is a `CG` motif model.

The `5mC` all-context model will return predictions at all `C` positions while the `5mCG` model
returns predictions on only `CG` motifs. Given the sequence `ACGTCA` the `5mC` model
predicts at all `C` bases `aCgtCa`. The `5mCG` model returns predictions at the only `CG`
motif `aCgtca`.

### SAM tags `MM` / `ML`

The SAM tags [specification](https://samtools.github.io/hts-specs/SAMtags.pdf) has a detailed
section on "Base Modifications" which describes in detail how modifications are annotated in
the SAM/BAM output from Dorado.

### Post processing

[Modkit](https://github.com/nanoporetech/modkit) is a tool for working with modified bases.
Documentation for Modkit can be found [here](https://nanoporetech.github.io/modkit/).

---

## Usage

Both Dorado `basecaller` (simplex) and `duplex` tools support modified basecalling
and they share a common interface for selecting which modifications to call.

The CLI arguments used to control which modified base models run are shown in the [simplex]({{find("simplex")}}#cli-reference)
and [duplex]({{find("duplex")}}#cli-reference) CLI references and the relevant *and shared* sections of which has been copied below:

```text
Modified model arguments:
  --modified-bases            A **space separated** list of modified base codes. Choose from:
                                pseU, 5mCG_5hmCG, 5mC, 6mA, 5mCG, m6A_DRACH, m6A, 5mC_5hmC, 4mC_5mC.
                                // More modified base model may be available

  --modified-bases-models     A **comma separated** list of modified base model paths.
  --modified-bases-threshold  The minimum predicted methylation probability for a modified base
                                to be emitted in an all-context model, [0, 1].
```

Please see the [models list]({{find("list")}}) for the complete set of canonical and modified base
basecalling models.

### Selecting modified base models

There are three ways to select modified base models:

#### Via model complex

!!! tip inline end  "Recommended"

Please refer to the model complex [documentation]({{find("complex")}})
which contains [examples]({{find("complex")}}#examples-of-model-complexes) of both canonical
and modified base model selection.

#### Via `--modified-bases` CLI argument

!!! Example inline end "Space Separated"

    Multiple modified base model **codes** must be **space separated**.

Similarly to how the model complex functions, the `--modified-bases` argument takes a **space separated**
list of modification codes and automatically resolves which modified base model to use based on your **simplex**
basecalling model selection. The modified base model selected will always be the **latest** available
as there is no way to specify a version (unlike when using model complex).

Examples:

```dorado
dorado basecaller hac         reads/  --modified-bases pseU      > calls.bam
dorado basecaller hac         reads/  --modified-bases 6mA 5mC   > calls.bam
dorado duplex /simplex/model/ reads/  --modified-bases 5mC       > calls.bam
```

#### Via `--modified-bases-models` CLI argument

!!! Example inline end "Comma separated"

    Multiple modified base model **paths** must be **comma separated**.

Similarly to how canonical basecall models can be specified using a filepath to an
existing simplex model, modified base models can be specified via a filepath using the
`--modified-bases-models` argument.

See also documentation for the [model downloader]({{find("downloader")}}).

```dorado
# Download the models
dorado download --model rna004_130bps_hac@v5.0.0
dorado download --model rna004_130bps_hac@v5.0.0_m6A@v1
dorado download --model rna004_130bps_hac@v5.0.0_pseU@v1

# Run the basecaller
dorado basecaller rna004_130bps_hac@v5.0.0 reads/ \
    --modified-bases-models rna004_130bps_hac@v5.0.0_m6A@v1,rna004_130bps_hac@v5.0.0_pseU@v1 \
    > calls.bam
```

### Modified bases threshold

The `--modified-bases-threshold` argument takes a value (float) in the interval `[0, 1]`
and controls how the `ML` and `MM` sam tags are written to the output.
Specifically, it sets the *probability* threshold that a modification must exceed
to be written to the output. It has no effect on the modification probabilities.

For example, if we were mod basecalling `5mC` and the `--modified-bases-threshold` were set to `0`
we could generate

```text
MM:Z:C+m?,0,0,0,0,0; ML:B:C,1,63,127,32,255
```

Note that there are no skipped positions (non-zero values) in the `MM` tag.

Setting `--modified-bases-threshold 0.45` would mean that the modified base probabilities below
`0.45 * 256 := 115` (converting to int8) are omitted from the output resulting in the
following SAM tags:

```text
MM:Z:C+m?,2,1; ML:B:C,127,255
```
