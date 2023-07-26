# Installation
cachetoolz is available from [PyPI](https://pypi.org/project/cachetoolz/) and can be installed by running

```bash
pip install cachetoolz
```

## Bundles

Cachetoolz also defines a group of bundles that can be used to install cachetoolz and the dependencies for a given feature.

You can specify these in your requirements or on the pip command-line by using brackets. Multiple bundles can be specified by separating them by commas.
```bash
pip install cachetoolz[redis]
pip install cachetoolz[redis,mongo]
```

The following bundles are available:

### Backends
* `cachetoolz[redis]`: for using Redis as a backend.
* `cachetoolz[mongo]`: for using Mongo as a backend.
