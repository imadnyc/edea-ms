# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2024-05-xx

### Added

- Automatic migrations with alembic. On startup edea-ms will check if there are outstanding migrations with alembic and
  apply them if necessary.
- value_hidden flag for forcing conditions to hide values which aren't relevant in the UI and export

### Changed

- Bump version number to 0.2.0
- UI: upgrade to superforms 2.x
- Updated UI and backend dependencies

## [0.1.2] - 2024-02-09

- Last release without changelog.
