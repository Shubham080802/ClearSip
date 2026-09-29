# Online-image collection and review

This workflow discovers references for every catalog recognition target. It does
not turn search metadata into accepted labels or activate a visual model.
See [source/API research](research/off-image-collection-api.md) and
[photo/model rights research](research/online-packaging-images.md).

## Bounded collection

Initial run: one 7UP-family search succeeded and an initial reference is
quarantined. Subsequent Aquafina and Powerade searches returned HTTP 503, so
remaining searches are incomplete. An earlier `7up Free` metadata candidate was
rejected for the regular 7UP class; the retained reference still needs exact US
identity and rights review. No samples have been approved or trained. Check the
[audit summary](../data/recognition/online-image-coverage.json) for the snapshot.

```bash
.venv/bin/python scripts/collect_online_images.py \
  --download-limit 24 --summary data/recognition/online-image-coverage.json
```

The collector uses one documented US-country/brand search per supported family,
at most 12 results per search (22 families, at most 264 records). Requests are
spaced at least seven seconds apart, with an identifying User-Agent and verified
TLS. Successful responses are cached. This is a bounded first-page audit,
**not an exhaustive survey**. A no-match does not prove photos do not exist;
brand aliases and omitted pages remain gaps. New unsupported brands are marked,
not silently assigned to another brand. Broad family leads need exact variants.

HTTP 401/403/429/503 stops further searches in that run. Do not evade access
restrictions or repeatedly retry. After the service permits access again,
resume with the cached responses; `--only-brand powerade` limits new requests
to one family. All targets remain in the output, including those not searched.

Images use OFF's documented AWS mirror rather than bulk server scraping, with
a 30-image cap, bounded responses, fixed approved host/path, no redirects, and
SHA-256 hashes. Missing images remain missing; recent uploads may not yet be
in the monthly mirror. One raw original behind a front image is one source
group: selected crops and resolutions are not extra independent examples.

The ignored `training-data/off-discovery/` directory contains:

- `cache/`: attributed source responses and actual retrieval timestamps.
- `audit.json`: candidate product metadata, source links, licenses, and gaps.
- `quarantine/` and `quarantine.json`: downloaded, **unapproved** references.
- `runs/`: retained audit/inventory snapshots for subsequent collection runs.
- `manifest.json`: initially empty; collection never adds training samples.

`--offline` rebuilds an audit from caches without new metadata queries. Keep
`--download-limit 0` as well for a fully offline run. The committed summary
contains only audit outcomes/counts, not the photos or source product database.

## Promote only genuinely reviewed samples

1. Inspect the actual photo. Confirm exact flavor/formulation, US package,
   size/container, and observed packaging design against source evidence.
   Country tags and barcode/name fields alone are not verification. Reject
   other-market designs, ambiguous photos, and regular/zero/diet conflicts.
2. Review image rights and intended training/model-distribution use. Preserve
   OFF/product-page attribution, license/version, contributor credit and
   source ID. Image CC BY-SA is separate from metadata ODbL and code MIT.
   Packaging artwork and other third-party rights are not automatically cleared.
3. Decode and review image quality; reject unrelated personal information,
   wrong subjects, unusable angles, exact duplicates and near-duplicates.
4. Add a reviewed `licensed_online` sample using the template in
   `data/recognition/photos.example.json`. The validator requires specific
   identity/rights reviewers and review records, source and license evidence,
   source groups, and actual file hashes. Don't invent a physical bottle ID or
   camera session from an online contributor name. Review fields are declarations,
   not automated legal proof; never fill them merely to bypass a gate.
5. Online references can seed **train** only. Independent real-camera
   validation/test images are still required. Derivative crops and augmented
   versions must stay with their original source group.

```bash
.venv/bin/python scripts/recognition_audit.py \
  --manifest training-data/off-discovery/manifest.json \
  --image-root training-data/off-discovery
```

The existing 100 train / 20 validation / 30 test starting targets still apply per
class, along with unknown examples, cumulative class retention, per-class gates,
and browser review. See [visual training](VISUAL_RECOGNITION.md). No training or
deployment occurs simply because a photo has been downloaded.
