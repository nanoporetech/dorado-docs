# Models

Dorado basecalling relies upon machine learning models to decode the raw nanopore sequencing
data. There are a number of factors which define a basecalling model but these can be broadly summarised
by their architecture which is often the defining factor for performance and accuracy, and
the training data that was used to train the model, which defines what the model is capable of accurately
decoding.

## Understanding Model Names

The names of Dorado models are systematically structured, each segment
corresponding to a different aspect of the model, which include both chemistry and
run settings (defined [here](#sequencing-condition)). Below are some examples of simplex basecalling models:

```text
dna_r10.4.1_e8.2_400bps_sup@v5.0.0
rna004_130bps_hac@v5.0.0
dna_r9.4.1_e8_fast@v3.4
```

```text
{analyte}_{pore}_{chemistry}_{speed}@version
```

### Speed and Accuracy

Typically for each model generation, 3 models are available and are named `fast`, `hac`
(high-accuracy), and `sup` (super-accurate). These are in order of increasing basecalling
accuracy where `fast` is the least accurate and `sup` is the most accurate.  In general,
larger models are more accurate but are more computationally expesinve to evaluate.

As such, **we recommend the `hac` model for most users**
as it strikes a good balance between accuracy and computational cost.

### Model Version Numbers

!!! tip inline end

    We recommend that users use the **latest** models for the best results.

Basecalling models are frequently updated to improve accuracy and performance. The model version
is identified using the following form `v{major}.{minor}.{patch}` for example `v4.3.0`.

Simplex basecalling models are identified by only one version but modification model names
contains two version numbers for example: `dna_r10.4.1_e8.2_400bps_hac@v4.3.0_6mA@v1` and follow
the format: `{simplex_model@version}_{modification@version}`

This is because **all modification models are paired with a specific simplex model**.
The first version identifies the simplex model while the second identifies the version of the
modification model. As such, modification model version numbers are reset on each simplex model
update.

For example, a `6mA@v1` modification model compatible with the `v4.3.0` simplex model
is more recent than a `6mA@v2` modification model compatible with  a`v4.2.0` simplex model.

### Sequencing Condition

Models are trained on carefully curated datasets for  specific nanopore sequencing condition and
as such they are each assigned specific names to denote which condition they are paired.

The sequencing condition will typically denote the following features:

Analyte Type - `dna / rna002 / rna004`

:   This denotes the type of analyte being sequenced. For DNA sequencing, this will be `dna`. If you are using a Direct RNA Sequencing Kit, this will be `rna002` or `rna004`, depending on the kit.

Pore Type - `r9.4.1 / r10.4.1`

:   This section corresponds to the type of flow cell used. For instance, `FLO-MIN114 / FLO-FLG114` is
indicated by `r10.4.1`, while `FLO-MIN106D / FLO-FLG001` is signified by `r9.4.1`.

Chemistry Type - `e8 / e8.2`

:   This represents the chemistry type, which corresponds to the kit used for sequencing. For example, Kit 14 chemistry is denoted by `e8.2` and Kit 10 or Kit 9 are denoted by `e8`.

Translocation Speed - `130bps / 260bps / 400bps`:

:   This parameter, defines the speed of translocation.