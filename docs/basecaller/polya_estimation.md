# Poly(A) Estimation

Dorado has initial support for estimating poly(A) tail lengths for cDNA (PCS and PCB kits) and RNA,
and can be configured for use with custom primer sequences, interrupted tails, and plasmids.

!!! info "Poly(A) and Poly(T)"

    Oxford Nanopore cDNA reads are sequenced in two different orientations and Dorado
    poly(A) tail length estimation handles both (A and T homopolymers).

This feature can be enabled by setting `--estimate-poly-a` argument which is disabled by default.

The estimated tail length is stored in the `pt:i` tag of the output record.
Reads for which the tail length could not be estimated will not have the `pt:i` tag.

Dorado **does not** edit the original basecalled sequence using the results of the poly(A/T) estimate.

## Custom poly(A) tail configuration

The default settings for this feature are optimized for non-interrupted poly(A/T)
sequences that occur at read ends but these setting can be configured using a configuration file
which is passed into Dorado using the `--poly-a-config` argument.

This configuration file can configure parameters for:

* Custom primer sequence for cDNA tail estimation
* Clustering of interrupted poly(A/T) tails
* Estimation of poly(A/T) length in plasmids

## Poly(A/T) reference diagram

```text title="cDNA"
 5' --- ADAPTER --- FRONT_PRIMER
... --- cDNA
... --- poly(A) --- RC(REAR_PRIMER) --- 3'

OR

 5' --- ADAPTER --- REAR_PRIMER  --- poly(T)
... --- RC(cDNA)
... --- RC(FRONT_PRIMER) --- 3'
```

```text title="dRNA"
3' --- ADAPTER --- poly(A) --- RNA --- 5'
```

```text title="Plasmid"
 5' --- ADAPTER
... --- DNA
... --- FRONT_FLANK --- poly(A) --- REAR_FLANK
... --- DNA --- 3'

OR

 5' --- ADAPTER
... --- RC(DNA)
... --- RC(REAR_FLANK) --- poly(T) --- RC(FRONT_FLANK)
... --- RC(DNA) --- 3'
```

## Configuration format

The poly(A) configuration file uses the `toml` format.

The content of the file depends on the application i.e. cDNA or plasmids.

=== "cDNA"

    ```toml title="polya_config.cdna.toml"
    [anchors]
    front_primer = "ATCG"
    rear_primer = "CGTA"
    primer_window = 150

    [threshold]
    flank_threshold = 0.6

    [tail]
    tail_interrupt_length = 10
    ```

=== "Plasmid"

    ```toml title="polya_config.plasmid.toml"
    [anchors]
    plasmid_front_flank = "CGATCG"
    plasmid_rear_flank = "TGACTGC"
    primer_window = 150

    [threshold]
    flank_threshold = 0.6

    [tail]
    tail_interrupt_length = 10
    ```

### Overrides

Configuration options can be overridden for individual barcodes. We generate a default
configuration as normal, and then add overrides of specific values for each barcode by
adding an `[[overrides]]` section labelled by the barcode name.

```toml title="polya_config.toml"
[anchors]
front_primer = "ATCG"
rear_primer = "CGTA"
[threshold]
flank_threshold = 0.6
[tail]
tail_interrupt_length = 5

[[overrides]]
barcode_id = "Custom-Kit_barcode01"
[overrides.threshold]
flank_threshold = 0.5       # overrides 0.6

[[overrides]]
barcode_id = "Custom-Kit_barcode02"
[overrides.anchors]
front_primer = "AACC"       # overrides ATCG
rear_primer = "GGTT"        # overrides CGTA
[overrides.tail]
tail_interrupt_length = 10  # overrides 5
```

This creates three configurations:

* a default configuration with custom front and rear primers and an interrupt length of 5
* a configuration to use for `barcode01` from kit `Custom-Kit` almost identical to the main custom settings (i.e. with the custom front and rear primers and the interrupt length), with an additional change to the `flank_threshold`.
* a configuration to use for `barcode02` from kit `Custom-Kit` with different primers and an interrupt length of 10, but with no change to the flank threshold.

### Configuration options

| Config Group | Option | Description |
| -------: | -- | -- |
| anchors | front_primer | Front primer sequence for cDNA^[1]^ |
| anchors | rear_primer | Rear primer sequence for cDNA^[1]^ |
| anchors | plasmid_front_flank | Front flanking sequence of poly(A) in plasmid^[2]^ |
| anchors | plasmid_rear_flank | Rear flanking sequence of poly(A) in plasmid^[2]^ |
| anchors | primer_window | Window of bases at the front and rear of the rear within which to look for primer sequences |
| threshold | flank_threshold  | Threshold to use for detection of the flank/primer sequences. Equates to `(1 - edit distance / flank_sequence)` |
| tail | tail_interrupt_length | Combine tails that are within this distance of each other (default is 0, i.e. don't combine any) |

1. For cDNA only - Values ignored if either `plasmid_front_flank` or `plasmid_rear_flank` are set.
2. For plasmids only
