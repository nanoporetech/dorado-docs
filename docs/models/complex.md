
# Model Selection Complex

!!! quote inline end "Definition of Complex"

    Consisting of many different and connected parts.

The `model` argument in Dorado tools can specify either a simplex model **path** or a model **_complex_**.

Using a model complex instructs Dorado to automatically select all basecalling models based on
the model complex given and the **data** to be basecalled. This includes the simplex models, modified bases
models and stereo duplex models.

## Model complex syntax

A model complex must start with the **simplex model speed**, and follows this syntax:

```text hl_lines="1"
speed[version][,mod[version]]*
```

* `[]` - Square brackets enclose an **optional** field.
* `*`  - The asterisk / star shows that a field may be repeated **zero or more times**.
* `,`  - All items must be **comma-separated**.

### Fields

#### _speed_

The model speed can be any of `fast`, `hac` or `sup`.

#### _version_

The `version` takes the form of `@vX.Y.Z` **or** `@latest`.

`X`, `Y` and `Z` here are major, minor, and patch version numbers (e.g. `@v1.2.3`).

Any missing values are assumed to be zero e.g. `@v1.2 -> @v1.2.0`.

If `@latest` is used, the latest available model version is used.

#### _mod_

!!! tip inline end "Multiple Modification Models"

    More than one modification model may be selected at once and each must be
    separated by a comma.

    For example: `sup,6mA,5mC@latest`

The `mod` field can be any modification name which is available for the simplex model
and can be optionally followed by a `version`.

Examples: `6mA`, `m6A`, `pseU`, `5mC@v2` and `5mCG_5hmCG@v1.0.0`.

Automatically selected **modification** models will always match the base simplex model version
and will be the latest compatible version unless a specific version is set by the user.

!!! warning "Multiple modification models must use different canonical bases"

    When selecting multiple modification models, only one modification per canonical base
    may be active at once.

    For example, `sup,4mC,5mC` is invalid as **both** modification models operate on
    the `C` canonical base context.

    This is because the modification probabilities reported could be nonsensical as each model
    could report high confidence of two different modifications at the same position.

See the [Model List](list.md) for a list of all available models.

## Examples of model complexes

| Model Complex | Description |
| :------------ | :---------- |
| `fast`  | Latest compatible **fast** model |
| `hac`  | Latest compatible **hac** model |
| `sup`  | Latest compatible **sup** model |
| `hac@latest` | Latest compatible **hac** simplex basecalling model |
| `hac@v4.2.0`  | Simplex basecalling **hac** model with version `v4.2.0` |
| `hac@v3.5` | Simplex basecalling **hac** model with version `v3.5.0` |
| `hac,5mCG_5hmCG`  | Latest compatible **hac** simplex model and latest **5mCG_5hmCG** modifications model for the chosen basecall model |
| `hac,5mCG_5hmCG@v3`  | Latest compatible **hac** simplex model and **5mCG_5hmCG** modifications model with version `v3.0.0` |
| `sup,5mCG_5hmCG,6mA`  | Latest compatible **sup** model and latest compatible **5mCG_5hmCG** and **6mA** modifications models |

Here are some examples of model complexes in use:

```dorado
# Simplex basecalling
dorado basecaller hac                   reads/ > calls.bam # HAC simplex basecalling
dorado basecaller hac@v4.1.0            reads/ > calls.bam # HAC simplex with specific version

# Simplex modification basecalling
dorado basecaller sup,6mA               reads/ > calls.bam # SUP with modifications
dorado basecaller sup,6mA,5mCG_5hmCG    reads/ > calls.bam # Multiple modification models
dorado basecaller sup@v4.2.0,6mA@v1     reads/ > calls.bam # Setting versions

# Duplex basecalling
dorado duplex     sup@v4.1.0  reads/ > calls.bam # SUP duplex basecalling with specific version
dorado duplex     sup,5mC     reads/ > calls.bam # SUP duplex basecalling with modification model
```
