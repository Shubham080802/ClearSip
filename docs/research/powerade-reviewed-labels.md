# Powerade reviewed label batch

**Superseded scope correction (2026-09-26):** The manufacturer lists available
bottle sizes separately from its 12 fl oz nutrition serving and 28 fl oz
container text. This does not verify the legacy 20 fl oz SQL records as exact
package matches. The UI now uses `reviewed-labels-core.json` at variant scope;
its Orange statement also corrects the earlier flavor wording to **natural
flavors**. See [the current core audit](core-label-audit.md). The original
batch description below is retained as historical context, not certification.

Reviewed on 2026-09-26 for the United States, using Powerade's first-party
[product page](https://www.powerade.com/products/powerade).

## Included package-label records

- Powerade Grape — 20 fl oz bottle
- Powerade Lemon Lime — 20 fl oz bottle
- Powerade Orange — 20 fl oz bottle

The source presents a 12 fl oz (355 mL) Nutrition Facts serving for these
variants. Each reviewed record keeps the 20 fl oz package separate from the
12 fl oz nutrition serving and does not infer a servings-per-container value.

For each listed serving, the source declares 80 calories, 21 g total sugar,
21 g added sugar, and 240 mg sodium. Ingredient statements are retained with
source provenance. The ClearSip assessment marks the package as
`routine_intake_caution` because the 21 g added-sugar amount is 42% of the
50 g Daily Value; this is label context, not an individualized health claim.

The first-party page also lists the following available sizes: Grape and
Lemon Lime in 20 and 28 fl oz; Orange in 12, 20, and 28 fl oz. The reviewed
database packages above cover 20 fl oz only. A distinct label version is still
required before presenting the other package sizes as reviewed.
