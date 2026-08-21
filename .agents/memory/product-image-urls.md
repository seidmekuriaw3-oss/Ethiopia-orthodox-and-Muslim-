---
name: Product image URL handling
description: Rules for rendering and importing product thumbnails from local paths or external URLs.
---

Product thumbnails may arrive as absolute HTTP(S) URLs or legacy local filenames. Rendering must preserve external HTTP(S) URLs and normalize local values under `static/uploads/products/` or `static/images/`. Imported catalogs should preferably download remote thumbnails into local storage so live contract checks and offline previews remain reliable.

**Why:** Concatenating every thumbnail with the static URL produced invalid paths such as `/static/uploads/products/https://...` and broke cart image rendering.

**How to apply:** Use the shared image-source helper in templates and run the normalization script after importing catalogs containing remote thumbnails.