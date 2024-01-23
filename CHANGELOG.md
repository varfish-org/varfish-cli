# Changelog

## [0.6.2](https://github.com/bihealth/varfish-cli/compare/v0.6.1...v0.6.2) (2024-01-23)


### Bug Fixes

* properly assign verison in release-please ([#91](https://github.com/bihealth/varfish-cli/issues/91)) ([52a0d79](https://github.com/bihealth/varfish-cli/commit/52a0d79477838647ef2919ac19ff3899e29324b4))
* version for release-please in CI ([#89](https://github.com/bihealth/varfish-cli/issues/89)) ([2aedb64](https://github.com/bihealth/varfish-cli/commit/2aedb6465237211133625ef19be601e43d47be9b))

## [0.6.1](https://github.com/bihealth/varfish-cli/compare/v0.6.0...v0.6.1) (2024-01-23)


### Continuous Integration

* install setuptools to fix "python sdist" in release-please ([#87](https://github.com/bihealth/varfish-cli/issues/87)) ([9b03c68](https://github.com/bihealth/varfish-cli/commit/9b03c687e34f9e94533fbd04f02b2d4baa65e759))

## [0.6.0](https://github.com/bihealth/varfish-cli/compare/v0.5.3...v0.6.0) (2024-01-23)


### Features

* add "projects project-list" command ([#50](https://github.com/bihealth/varfish-cli/issues/50)) ([057abd5](https://github.com/bihealth/varfish-cli/commit/057abd56667e2b089ee2d30a4c761fd4b67a7278))
* conversion from DRAGEN QC to legacy varfish format ([#85](https://github.com/bihealth/varfish-cli/issues/85)) ([#86](https://github.com/bihealth/varfish-cli/issues/86)) ([043dbc3](https://github.com/bihealth/varfish-cli/commit/043dbc3437dfc2d938a3ba5a4a4ea91ffa12be4f))
* migrate argparse code to typer ([#48](https://github.com/bihealth/varfish-cli/issues/48)) ([#61](https://github.com/bihealth/varfish-cli/issues/61)) ([d1c86d4](https://github.com/bihealth/varfish-cli/commit/d1c86d43be19b66c5f3429c62772e2febadf119c))
* migration from attrs to pydantic ([#49](https://github.com/bihealth/varfish-cli/issues/49)) ([#65](https://github.com/bihealth/varfish-cli/issues/65)) ([2c9e402](https://github.com/bihealth/varfish-cli/commit/2c9e402b66731e35f2214eaca52d3ae49069613b))


### Documentation

* installation instructions in manual ([#69](https://github.com/bihealth/varfish-cli/issues/69)) ([0afb87c](https://github.com/bihealth/varfish-cli/commit/0afb87c377ebda2f50892afff4ab857bce34e4a9))
* updating README, adding terraform docs ([#68](https://github.com/bihealth/varfish-cli/issues/68)) ([f6dd1bf](https://github.com/bihealth/varfish-cli/commit/f6dd1bf850d3f1ac8637f15d165ac262d1f93b2b))

## [0.5.3](https://github.com/bihealth/varfish-cli/compare/v0.5.2...v0.5.3) (2023-07-17)


### Features

* force release of 0.6 ([#46](https://github.com/bihealth/varfish-cli/issues/46)) ([f003be8](https://github.com/bihealth/varfish-cli/commit/f003be8b1f953ff4ab22f7d274264747dd39870d))


### Bug Fixes

* allow varfish upload without SV effects ([#43](https://github.com/bihealth/varfish-cli/issues/43)) ([4aead65](https://github.com/bihealth/varfish-cli/commit/4aead65054e97adf7564f8fb3d3a3e0db755c34f))
* fixing issue with logging ([ab62f24](https://github.com/bihealth/varfish-cli/commit/ab62f242445150c2472aa45ea0c0f6d7782a7b8c))

### [0.5.2](https://www.github.com/bihealth/varfish-cli/compare/v0.5.1...v0.5.2) (2023-07-17)


### Bug Fixes

* allow varfish upload without SV effects ([#43](https://www.github.com/bihealth/varfish-cli/issues/43)) ([4aead65](https://www.github.com/bihealth/varfish-cli/commit/4aead65054e97adf7564f8fb3d3a3e0db755c34f))
* Fixing case list API ([#37](https://www.github.com/bihealth/varfish-cli/issues/37)) ([ccaccfc](https://www.github.com/bihealth/varfish-cli/commit/ccaccfcbec7fb209492f1855b5e740f20ac60bbc))

### [0.5.2](https://www.github.com/bihealth/varfish-cli/compare/v0.5.1...v0.5.2) (2023-06-12)


### Bug Fixes

* Fixing case list API ([#37](https://www.github.com/bihealth/varfish-cli/issues/37)) ([ccaccfc](https://www.github.com/bihealth/varfish-cli/commit/ccaccfcbec7fb209492f1855b5e740f20ac60bbc))

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
