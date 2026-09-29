# Visual recognition: full coverage in staged batches

## Current state

The recognition target registry includes every current discovery and package-only
variant: **86 targets, 83 concrete drinks, and three broad family leads**.
The additional target is Monster Energy Zero Sugar, distinct from Monster Ultra.
**Zero visual classes are trained or deployed.** No images have been approved
for training. Online reference discovery is now available, with all
downloads quarantined until identity and rights review. Browser OCR still reads
text; it is not a trained packaging model. See [online collection](ONLINE_IMAGE_COLLECTION.md).

`/api/recognition-coverage` derives targets from SQL, so newly added records are
registered automatically rather than excluded from a fixed pilot list.
Image matching is separate from ingredient availability: recognizing a product
does not create a missing ingredient panel or certify its package/recipe.

## Coverage and batches

The first collection priority is 12 specific variants: Coca-Cola Original,
Zero Sugar and Cherry; Pepsi, Diet Pepsi and Pepsi Zero; Sprite; Powerade Grape,
Orange and Zero Mixed Berry; Gatorade Cool Blue; and Monster Energy Zero Sugar.
All other concrete entries remain in the registry with collection priority two.
Snapple, Bai, and LaCroix currently represent broad families; define exact
flavors/package designs before using them as model classes.

Run the complete coverage audit (no ML dependencies required):

```bash
.venv/bin/python scripts/recognition_audit.py
```

Camera testing is deferred at the user's request. Continue collection, identity/
rights review, and training preparation without marking camera evaluation passed.
Get per-target train/validation/test deficits and source/session group counts:

```bash
.venv/bin/python scripts/recognition_audit.py --preparation \
  --manifest training-data/off-discovery/manifest.json \
  --image-root training-data/off-discovery
```

This includes all targets plus unknown scenes, excludes broad family leads from
training, and counts only manifest samples after permission/checksum/leakage
validation. Quarantined references do not count. Group counts help expose
repeated sources; they do not establish image diversity or legal clearance.

Registration is not training. The path is: target registered → photo collection
→ ready to train → candidate model → per-class evaluation → browser review
→ validated deployment. Every specific drink is an eventual coverage target;
partial releases must show their actual coverage. There is no claim that a
finite model recognizes every unseen packaging design.

## Collect usable, permission-cleared photos

Store original photos and a manifest under the ignored `training-data/` directory,
not in GitHub. Copy the structure in `data/recognition/photos.example.json` into
your private manifest and populate `samples` with real records. The `sample_fields`
object is only an example and does not count as a training image.

Each sample identifies a stable registry class ID, relative file path, SHA-256,
train/validation/test split, capture session, physical bottle/can ID, and
documented permission for training and model distribution. The unknown class
ID is `__unknown__`: collect out-of-catalog drinks, empty scenes, and other objects.
Licensed online references use a separate template with original-image grouping,
attribution, exact-identity review, rights review, and model-distribution review.
They are allowed only in the training split; independent camera holdouts remain
required. The collector never approves those fields or invents camera provenance.
Do not use public manufacturer photographs as if visibility grants permission.
Owning a photograph does not automatically settle rights in packaging artwork;
review uncertain uses. Exclude people/private information; do not silently retain
users' ordinary scans as training photos.

Initial collection gates are **100 training, 20 validation, and 30 test images
per specific class and for unknown scenes**. These are project starting targets,
not an accuracy guarantee. Vary lighting, glare, viewpoints, backgrounds,
devices, packaging revisions, and independent specimens. Extra adjacent video
frames do not substitute for independent observations.

Keep each capture session and each physical specimen entirely in one split.
Hashes reject exact duplicates; near-duplicates and derivative crops must be
assigned to the same session/specimen. The audit checks identity, checksums,
permissions, paths, and split leakage. It does not prove legal clearance or image
quality; actual decoding and human label review remain necessary.

```bash
.venv/bin/python scripts/recognition_audit.py \
  --manifest training-data/manifest.json --image-root training-data/images
```

## Train cumulatively in Python

The proposed training/export dependencies are separate from Vercel's API.
Use an isolated **Linux Python 3.11** environment/notebook. The candidate package
versions are in `ml/requirements-training.txt`; this heavy environment has not
been installed or smoke-tested yet because no photos have been supplied.
Resolve/lock transitive packages, run `pip check`, and verify imports before use.
See the [primary-source compatibility research](research/visual-recognition-training.md).

Install the training requirements in that isolated environment, then run:

```bash
python scripts/train_recognizer.py \
  --manifest training-data/manifest.json --image-root training-data/images \
  --output ml-artifacts/batch-001 --plan-only

python scripts/train_recognizer.py \
  --manifest training-data/manifest.json --image-root training-data/images \
  --output ml-artifacts/batch-001
```

The plan refuses empty/insufficient data before importing TensorFlow. Training
uses pretrained MobileNetV2 with a new classification head and all ready classes.
Previously released classes cannot be dropped: retain their photos and include
them when adding each new burst. Explicitly supply `--previous-release` when
continuing from an external/candidate release rather than the deployed manifest.
ImageNet weights are downloaded by the training library; review upstream model
terms before redistribution. The initial script does not perform augmentation
or fine-tuning beyond the head; evaluate whether they are needed after real data.

The classifier outputs ordered catalog IDs plus unknown—not ingredients or
health assessments. TensorFlow and the browser use RGB 224×224, bilinear
half-pixel resizing, and scaling to [-1, 1]. Label order and preprocessing are
part of the artifact contract.

### Experimental training while camera evaluation is deferred

Use `--training-mode research-only` to train an **unapproved experimental
candidate** once at least two concrete classes and unknown scenes each have
100 approved training images. This mode retains permission/provenance checks
and previously released/candidate classes, but does not require camera holdouts
to start training. It never decodes holdout images for fitting/evaluation, tunes rejection
thresholds, or reports camera accuracy. No current data meets these requirements.

```bash
python scripts/train_recognizer.py \
  --manifest training-data/off-discovery/manifest.json \
  --image-root training-data/off-discovery \
  --output ml-artifacts/research-001 --training-mode research-only --plan-only
```

Manifest integrity checks still verify every listed file's checksum and split
provenance; this is not model evaluation or test-set tuning.

Remove `--plan-only` only in the verified isolated training environment, after the
data requirements pass. Experimental artifacts carry `training_mode:
research-only`, `evaluation_status: deferred`, null rejection thresholds and
failed/unperformed held-out gates. Both CI release validation and browser
inference reject them, even if someone changes just the status flag.

When camera testing resumes, collect independent validation/test sessions and
create a **new camera-evaluated run** (the default mode), retaining existing
classes with `--previous-release ml-artifacts/research-001/release.json`.
Do not relabel the experimental artifact as validated. Training/export itself
remains unexercised until approved photos and a verified ML environment exist.

## Evaluate and release honestly

Validation images tune score/margin rejection thresholds. Untouched test sessions
then evaluate every class: initial gates are precision ≥95%, recall ≥80%, at least
30 test images per class, and unknown false acceptance ≤5%. These are release
targets, not guaranteed performance or calibrated probabilities. Inspect
regular/zero and flavor confusion, and test unknowns beyond those used in training.
If you repeatedly use a test set to make changes, collect a new independent
holdout for the next release decision.

The script exports **candidate** artifacts even when test gates fail, never
directly to public assets. Candidate files cannot activate browser inference.
Check converter parity with:

```bash
node scripts/check_model_parity.mjs ml-artifacts/batch-001
```

This checks TF.js CPU predictions against a Python numerical reference; it does
not replace browser/device testing. In an isolated preview, review actual Chrome
and mobile camera images, latency, memory, tensor disposal, unknown rejection,
conflicting label text, offline failures, and rendering of confirmed results.
Record the tested model version and artifact SHA-256, reviewer, device list, score differences, and
outcome in `browser-review.json`. Do not invent passing evidence.

Only after the evidence passes, copy the reviewed `model.json`, all weight
shards, `evaluation.json`, `browser-review.json`, and release metadata together
to `public/models/drink-recognizer/`, set status `validated` and
`validation_passed: true`, and run `scripts/check_recognizer_release.py` plus CI.
Retain the previous version for regression/rollback. Source/model license review
is a separate release requirement; test accuracy does not grant rights.

## Browser behavior

Camera, image, and video-frame scans try an optional native barcode reader,
then local OCR and a lazily loaded visual model when one is validated. Unsupported
barcodes, missing models, conflicts, and uncertain scores fall back to text/manual
selection. Browser performance depends on the device; the model is not currently
continuous live detection. Unknown rejection is a safeguard, not a guarantee.

Suggestions always require user confirmation before stable-ID database lookup
and package-size selection. Size and reformulations are not inferred from
appearance. Images are not uploaded to the API or saved for training by default.
The trained model should identify packaging; sourced database records supply
the explanation.
