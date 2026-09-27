# Third-party notices

ClearSip's MIT license applies to its original work, not to the components below.
This is a direct-dependency/resource inventory, **not a complete transitive
license audit or a replacement for upstream license texts**. Versions below
were inspected in the local installation on September 26, 2026; production
Python resolutions may differ because requirements use minimum versions.

| Component | Inspected version | Declared license | Upstream project |
| --- | --- | --- | --- |
| Vite (build tooling) | 7.3.6 | MIT | [vitejs/vite](https://github.com/vitejs/vite) |
| Tesseract.js | 7.0.0 | Apache-2.0 | [naptha/tesseract.js](https://github.com/naptha/tesseract.js) |
| Tesseract.js core | 7.0.0 | Apache-2.0 | [naptha/tesseract.js-core](https://github.com/naptha/tesseract.js-core) |
| FastAPI | 0.141.1 | MIT | [fastapi/fastapi](https://github.com/fastapi/fastapi) |
| Uvicorn | 0.53.0 | BSD-3-Clause | [Kludex/uvicorn](https://github.com/Kludex/uvicorn) |
| Psycopg / psycopg-binary | 3.3.6 | LGPL-3.0-only | [psycopg/psycopg](https://github.com/psycopg/psycopg) |
| Certifi | 2026.7.22 | MPL-2.0 | [certifi/python-certifi](https://github.com/certifi/python-certifi) |
| DM Sans | Hosted font | OFL-1.1 | [Font license](https://github.com/google/fonts/blob/main/ofl/dmsans/OFL.txt) |
| DM Mono | Hosted font | OFL-1.1 | [Font license](https://github.com/google/fonts/blob/main/ofl/dmmono/OFL.txt) |
| Playfair Display | Hosted font | OFL-1.1 | [Font license](https://github.com/google/fonts/blob/main/ofl/playfairdisplay/OFL.txt) |

The frontend requests fonts from Google Fonts. OCR uses Tesseract resources
loaded through jsDelivr; language data and components bundled by upstream
packages require their own release-specific review. Browser speech recognition
is a browser/platform service, not code licensed by ClearSip.

For source or binary redistribution, inspect the actual installed artifacts,
including transitive packages, bundled libraries, fonts, OCR models, and any
NOTICE files. Keep required notices and license texts; review source-availability
and other obligations for the relevant licenses and distribution method.
In particular, do not assume Psycopg, its binary bundle, or Certifi becomes
MIT-licensed because ClearSip uses it. An upstream link alone is not a complete
redistribution compliance package.

`package-lock.json` records JavaScript resolutions. Python dependency declarations
are in `requirements.txt` and `pyproject.toml`. Refresh this inventory whenever
dependencies or externally loaded assets change.

Manufacturer data and brand names are addressed separately in
[Licensing and data rights](LICENSE_SCOPE.md).
