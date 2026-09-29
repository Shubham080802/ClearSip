# Visual recognition: training and browser deployment

Researched: 2026-09-28. These are implementation recommendations, not evidence that a ClearSip classifier has already been trained or that every catalog drink is visually recognizable.

## Recommended stack

Use **Python TensorFlow with legacy Keras, MobileNetV2 transfer learning, and TensorFlow.js Layers inference in the browser**. Train a new drink-variant classification head on a frozen pretrained base; optionally fine-tune upper layers later at a lower learning rate. This follows TensorFlow's [transfer-learning workflow](https://www.tensorflow.org/tutorials/images/transfer_learning). The model returns catalog IDs, never ingredients or health advice; existing database records supply those details.

Start with RGB 224×224 inputs, identical resizing and MobileNetV2 preprocessing in Python and JavaScript, global-average pooling, and a softmax classification head. [MobileNetV2 documentation](https://www.tensorflow.org/api_docs/python/tf/keras/applications/MobileNetV2) specifies its input/preprocessing contract. Keep augmentation in the training data pipeline, not in the exported inference model; avoid custom/Lambda layers because the [TF.js Keras importer](https://www.tensorflow.org/js/tutorials/conversion/import_keras) supports standard serializable constructs rather than arbitrary Python code.

Export a Layers `model.json` and weight shards, plus explicit ordered catalog-ID labels and preprocessing/rejection metadata. Load with `tf.loadLayersModel`; serve all artifacts together at a versioned same-origin static path. This artifact layout and loader are documented in the [official importer](https://www.tensorflow.org/js/tutorials/conversion/import_keras). Browser inference keeps the camera frame local; only the selected product ID needs database lookup. This privacy arrangement is a ClearSip design decision, not an automatic property of any ML library.

## Environment and conversion caveats

Training/export belongs in a separate Linux Python 3.11 environment or controlled notebook, **not** the deployed FastAPI requirements. A conservative compatibility candidate is TensorFlow 2.16.2, `tf-keras` 2.16.0, TensorFlow.js converter 4.22.0, and TensorFlow Decision Forests 1.9.2. This environment has **not been installed or validated by this research**; resolve and lock all transitive dependencies and run `pip check`, import, export, and browser-load smoke tests before calling it reproducible.

Why this needs care: [converter 4.22 requirements](https://raw.githubusercontent.com/tensorflow/tfjs/tfjs-v4.22.0/tfjs-converter/python/requirements.txt) include `tf-keras>=2.16` and TF Decision Forests, even for a non-forest model. The [TF-DF compatibility table](https://www.tensorflow.org/decision_forests/known_issues) pairs 1.9.2 with TF 2.16.2. Do not combine converter 4.22 with TF 2.15 as an assumed clean pin set. Also pin a compatible JAX/Flax dependency set after resolver testing.

Use `tf_keras` directly or set `TF_USE_LEGACY_KERAS=1` before importing TensorFlow, as explained by [Keras](https://keras.io/keras_3/). The [converter's direct `save_keras_model` implementation](https://raw.githubusercontent.com/tensorflow/tfjs/tfjs-v4.22.0/tfjs-converter/python/tensorflowjs/converters/keras_h5_conversion.py) writes a legacy `.h5` intermediate. Do not assume standalone Keras 3 serialization produces an equivalent browser artifact. Validate numerical agreement between Python and actual browser predictions on the same reference images.

## Full-catalog coverage without misleading claims

Register every catalog entry from day one, but distinguish **registered**, **photos pending**, **training ready**, **trained**, and **validated**. Broad family placeholders need exact variant/package identity before creating a visual class. Include all previously learned classes in each expanded training/evaluation run; a small burst adds data, not a license to forget earlier drinks. Ship only classes that pass their own held-out checks, and expose remaining coverage honestly.

Collect multiple independent package specimens, sessions, devices, angles, backgrounds, glare, occlusion, and packaging revisions. Keep a specimen/session entirely in one train/validation/test split; neighboring video frames are not independent evidence. This applies the [grouped-validation principle](https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation-iterators-for-grouped-data). Hash duplicates and group derivative crops with their originals. Augment training only.

Use permission-cleared photos and retain ownership, permission/license evidence, attribution, source, and capture consent in the photo manifest. Public availability does not establish unrestricted rights: photographs are protected works under [Copyright Office guidance](https://www.copyright.gov/what-is-copyright/). Original photographs do not automatically resolve separate packaging-art/trademark issues. Do not extend the code's MIT license to third-party images; retain legal review for uncertain sources and uses.

## Acceptance and unknown rejection

Evaluate per-class precision/recall, regular-versus-zero/flavor confusions, top-three accuracy, unknown-drink/no-drink false acceptance, and mobile latency. Tune score and runner-up-margin thresholds on validation data, then evaluate once on untouched test sessions. Softmax scores are not guaranteed calibrated probabilities; see [probability calibration](https://scikit-learn.org/stable/modules/calibration.html). Out-of-distribution detection remains a separate problem even for confident classifiers; see the [ODIN research paper](https://arxiv.org/abs/1706.02690).

A background/unknown class and score thresholds are safeguards, not a guarantee against unseen packaging. Initially show candidate matches for user confirmation, with OCR as supporting evidence; conflicting Zero Sugar/flavor text must not silently select a product. Package size, UPC, and reformulation require barcode/label evidence or confirmation, not visual appearance alone.

Lazy-load the browser model, use asynchronous tensor reads, dispose tensors, and test low-memory devices. These memory/performance requirements follow the [TF.js platform guide](https://www.tensorflow.org/js/guide/platform_environment). Keep OCR/manual lookup available when a model is missing, incompatible, slow, or uncertain.
