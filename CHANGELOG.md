# Changelog

### [0.5.1](https://www.github.com/bihealth/varfish-cli/compare/v0.5.0...v0.5.1) (2023-02-09)


### Bug Fixes

* manifest for readme and changelog ([#35](https://www.github.com/bihealth/varfish-cli/issues/35)) ([f14d647](https://www.github.com/bihealth/varfish-cli/commit/f14d6472728995b9e18726fbfb7c36e86319c999))

## [0.5.0](https://www.github.com/bihealth/varfish-cli/compare/v0.4.0...v0.5.0) (2023-02-09)


### Features

* replace python-Levenshtein with polyleven ([#26](https://www.github.com/bihealth/varfish-cli/issues/26)) ([#32](https://www.github.com/bihealth/varfish-cli/issues/32)) ([73703bd](https://www.github.com/bihealth/varfish-cli/commit/73703bd73796b066de689954caa19a5767f97d76))


### Documentation

* fixing CI status badge ([#34](https://www.github.com/bihealth/varfish-cli/issues/34)) ([9967bbd](https://www.github.com/bihealth/varfish-cli/commit/9967bbd7a706d8338c188468a67a8bbebdb7a330))

## 0.4.0

- Adding support for varannos REST API (#24).

## 0.3.5

- Allowing to upload per-case gene annotation file (#20).
- Adding client endpoint for retrieving case from API (#18).

## 0.3.4

- Adding support for latest varfish-annotator output for svs (#16).

## 0.3.3

- Case importer distinguished smallvar and SV DB info files (#13).

## 0.3.2

- Fixing structuring/unstructuring of genomic region

## 0.3.1

- Allow disabling of `verify_ssl` in CLI

## 0.3.0

- Adding implementation of REST API (#7).

## 0.2.8

- Adding support to specify genome build on import (defaulting to GRCh37).

## 0.2.7

- Fix reading of non-compressed genotypes TSV file.

## 0.2.6

- Fixes to linting.

## 0.2.5

- Switching build system to Github Actions
- Adding many tests
- Fixing `verify_ssl` for case list.

## 0.2.4

- Added `--no-verify-ssl`.

## 0.2.3

- Added state field to `VariantSetImportInfo` class.
- Added endpoint for updating variant set import info.

## 0.2.2

- More `MANIFEST.in` fixes.

## 0.2.1

- Fixing package (`MANIFEST.in`).

## 0.2.0

- Adjusted to upstream REST API changes.
- Cases with all files can now be uploaded.

## 0.1.0

- everything is new
