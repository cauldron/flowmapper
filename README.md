# flowmapper

[![PyPI](https://img.shields.io/pypi/v/flowmapper.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/flowmapper.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/flowmapper)][pypi status]
[![License](https://img.shields.io/pypi/l/flowmapper)][license]

[![Read the documentation at https://flowmapper.readthedocs.io/](https://img.shields.io/readthedocs/flowmapper/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/fjuniorr/flowmapper/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/fjuniorr/flowmapper/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/flowmapper/
[read the docs]: https://flowmapper.readthedocs.io/
[tests]: https://github.com/fjuniorr/flowmapper/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/fjuniorr/flowmapper
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Flowmapper

This is a tool to automate matching elementary flow lists in life cycle assessment. It can map
different lists against each other and generate usable transformation files for those mappings.

It works by starting with the assumption that there is a core underlying ontology for elementary
flows, regardless of the expression of that ontology in difference data formats. Here is the core
ontology that `flowmapper` uses:

* name: str, the canonical name used to identify a substance, e.g. "1,4-Butanediol"
* identifier: str, or complex type with a string representation, the unique string used to identify the flow, unit, and context combination, e.g. "38a622c6-f086-4763-a952-7c6b3b1c42ba"
* context: tuple[str], a hierarchical organization into environmental compartments, e.g. `("air", "urban air close to ground")`
* unit: str, or complex type with a string representation, e.g. "kg"
* sector-specific labels: str, or complex type with a string representation, a set of additional fields which can help identify or further specify a flow, e.g. CAS number 000110-63-4
* synonyms: list[str], a list of alternative unique names for a substance, e.g. `["Butylene glycol", "butane-1,4-diol"]`. Synonyms should not overlap.

Flowmapper **assumes that the source and target lists are given in this format**; it comes with or plays well with conversion software for data formats like ecospold, FEDEFL, and SimaPro CSV.

Chemical formulas are not currently used - they can be expressed in too many different ways, and haven't proven useful for matching.

Matching across the two lists is defined by a set of strategy functions; matching can take some or
all ontological elements into account. Due to the sometimes chaotic nature of the input data,
matching usually needs to be customized for the specific source and target lists.

For example, a matching strategy could say that two flows are the same if their name and context are equal, or if their CAS number and context are equal. Units are rarely compared directly; instead, after a match is found we check that the units have [the same dimension](https://en.wikipedia.org/wiki/Dimensional_analysis), and apply unit conversions using [pint](https://pint.readthedocs.io/en/stable/) if necessary.

This library does not generate partial matches (i.e. "1,4-Butanediol" is always the same as "butane-1,4-diol", but the separate contexts would need to be matched afterwards). Partial matches could be used to reduce the size of the matching file, as one could store name matches in one partial match and context matches in another partial match, but we prefer the explicit enumeration of all matches of flows present in the source and target lists.

Matching is usually done by checking for equality. Instead of forcing conversion and then testing,
flowmapper comes with custom classes for these ontological elements which allow for a flexible
definition of equality, and the testing of logical relationships. For example, you can do this:

```python
from flowmapper import CAS
first = CAS("   007440-05-3")
second = CAS("7440-05-3")
first == second
>>> True
```

## Installation

You can install _flowmapper_ via [pip] from [PyPI]:

```console
$ pip install flowmapper
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [MIT license][License],
_flowmapper_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://flowmapper.readthedocs.io/en/latest/usage.html
[License]: https://github.com/fjuniorr/flowmapper/blob/main/LICENSE
[Contributor Guide]: https://github.com/fjuniorr/flowmapper/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/fjuniorr/flowmapper/issues
