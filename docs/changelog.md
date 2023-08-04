# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.1]
### Added
- Documentation
- Dependabot
- Pre-commit with gitlint

### Fixed
- Cache TTL (Time to Live) with timedelta
- Simple decorator ``@cache`` and ``@cache.clear`` receive the explicitly positional function

## [0.3.0] - 2023-07-20
### Feature
- Adds kwargs to receive and pass arguments to remote backend clients (redis and mongo)

## [0.2.0] - 2023-07-18
### Feature
- Bare decorator ``@cache`` and ``@cache.clear``

### Changed
- Decorator argument name cache from ``expire`` to ``ttl``
- The cache decorator only takes keyword arguments

[Unreleased]: https://github.com/taconi/cachetoolz/compare/0.3.1...HEAD
[0.3.1]: https://github.com/taconi/cachetoolz/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/taconi/cachetoolz/compare/0.2.0...0.3.0
[0.2.0]: https://github.com/taconi/cachetoolz/releases/tag/0.2.0
