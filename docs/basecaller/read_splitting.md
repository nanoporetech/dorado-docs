# Read Splitting

Dorado performs read splitting automatically.

When a single input read contains multiple concatenated reads, dorado basecaller will split the
original input read into separate subreads. This operation is performed by default for both DNA
and RNA.

Each subread has a new read id that is assigned by dorado.

The following tags can be used to associate a subread to its parent:

| Tag | Description |
| --- | ----------- |
| `pi:Z` | The parent read id that this subread was generated from. |
| `sp:i` | Maps the start of the subread's signal data to the corresponding location in the parent read's signal data. |
| `ns:i` | The number of samples corresponding to the subread after splitting. |
| `ts:i` | The number samples trimmed from the start of subread's signal after splitting. |
