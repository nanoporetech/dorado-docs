# SAM specification

## Header

```text
@HD  VN:1.6  SO:unknown
@PG  ID:basecaller PN:dorado VN:0.2.4+3fc2b0f CL:dorado basecaller hac pod5/ DS:gpu:Quadro GV100
```

## Read Group Header

|  Tag   | Description                                                                  |
| --:| ------------------------------------------------------------------------------------------ |
| `ID` | `<runid>_<basecalling_model>_<barcode_arrangement>`                                        |
| `PU` | `<flow_cell_id>`                                                                           |
| `PM` | `<device_id>`                                                                              |
| `DT` | `<exp_start_time>`                                                                         |
| `PL` | `ONT`                                                                                      |
| `DS` | `basecall_model=<basecall_model_name> modbase_models=<modbase_model_names> runid=<run_id>` |
| `LB` | `<sample_id>`                                                                              |
| `SM` | `<sample_id>`                                                                              |

## Read Tags

|  Tag   | Description                                                |
| ------:| -----------------------------------------------------------|
| `RG:Z:`  | `<runid>_<basecalling_model>_<barcode_arrangement>`        |
| `qs:f:`  | mean basecall q-score                                       |
| `ts:i:`  | the number of samples trimmed from the start of the signal |
| `ns:i:`  | the basecalled sequence corresponds to the interval `signal[ts : ns]` <br /> the move table maps to the same interval. <br /> note that `ns` reflects trimming (if any) from the rear <br /> of the signal. |
| `mx:i:`  | read mux                                                   |
| `ch:i:`  | read channel                                               |
| `rn:i:`  | read number                                                |
| `st:Z:`  | read start time (in UTC)                                   |
| `du:f:`  | duration of the read (in seconds)                          |
| `fn:Z:`  | file name                                                  |
| `sm:f:`  | scaling midpoint/mean/median (pA to ~0-mean/1-sd)          |
| `sd:f:`  | scaling dispersion  (pA to ~0-mean/1-sd)                   |
| `sv:Z:`  | scaling version                                            |
| `mv:B:`c | sequence to signal move table _(optional)_                 |
| `dx:i:`  | bool to signify duplex read _(only in duplex mode)_        |
| `pi:Z:`  | parent read id for a split read                            |
| `sp:i:`  | start coordinate of split read in parent read signal       |
| `bh:i:`  | number of detected bedfile hits _(only if alignment was performed with a specified bed-file)_ |
| `MN:i:`  | Length of sequence at the time MM and ML were produced     |

### Poly(A/T) Tags

When `dorado` is run with poly(A/T) estimation enabled, additional tags are added to each SAM record as follows:

* `pt:i` is the estimated poly(A/T) tail length in cDNA and dRNA reads
* `pa:B:i` is an array of signal positions related to the poly(A/T) estimation, in order:
    * The position in the signal used as the anchor for the poly(A/T) search
    * The start of the poly(A/T) region
    * The end of the poly(A/T) region
    * The the start of a secondary poly(A/T) region in the case of plasmids, (-1 otherwise or if not found)
    * The end of a secondary poly(A/T) region in the case of plasmids, (-1 otherwise or if not found)
