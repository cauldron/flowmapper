"""MatchCondition enum for representing match quality levels."""

from enum import StrEnum


class MatchCondition(StrEnum):
    """
    Enumeration of match quality conditions based on SKOS vocabulary.

    Match conditions represent the semantic relationship between source and target
    flows in a mapping. They follow the SKOS (Simple Knowledge Organization System)
    vocabulary for concept matching.

    Attributes
    ----------
    exact : str
        Exact match - the flows are semantically identical.
        SKOS URI: http://www.w3.org/2004/02/skos/core#exactMatch
    close : str
        Close match - the flows are very similar but not identical.
        SKOS URI: http://www.w3.org/2004/02/skos/core#closeMatch
    related : str
        Related match - the flows are related but not equivalent.
        SKOS URI: http://www.w3.org/2004/02/skos/core#relatedMatch
    narrow : str
        Narrow match - the target is more specific than the source.
        SKOS URI: http://www.w3.org/2004/02/skos/core#narrowMatch
    broad : str
        Broad match - the target is more general than the source.
        SKOS URI: http://www.w3.org/2004/02/skos/core#broadMatch

    Examples
    --------
    >>> condition = MatchCondition.exact
    >>> condition.as_glad()
    '='
    >>> condition = MatchCondition.related
    >>> condition.as_glad()
    '~'
    """

    exact = "http://www.w3.org/2004/02/skos/core#exactMatch"
    close = "http://www.w3.org/2004/02/skos/core#closeMatch"
    related = "http://www.w3.org/2004/02/skos/core#relatedMatch"
    # A triple <A> skos:broader <B> asserts that <B>, the object of the triple, is a broader concept
    # than <A>, the subject of the triple.
    narrow = "http://www.w3.org/2004/02/skos/core#narrowMatch"  # in SKOS the *target* is narrower than the *source*
    broad = "http://www.w3.org/2004/02/skos/core#broadMatch"  # in SKOS the *target* is broader than the *source*

    def as_glad(self) -> str:
        """
        Convert match condition to GLAD format symbol.

        GLAD (Global LCA Data Access) network uses single-character symbols
        to represent match conditions in flow mappings.

        Returns
        -------
        str
            Single character symbol:
            - "=" for exact match
            - "~" for close or related match
            - ">" for narrow match
            - "<" for broad match

        Examples
        --------
        >>> MatchCondition.exact.as_glad()
        '='
        >>> MatchCondition.related.as_glad()
        '~'
        """
        if self.value == "http://www.w3.org/2004/02/skos/core#exactMatch":
            return "="
        elif self.value == "http://www.w3.org/2004/02/skos/core#closeMatch":
            return "~"
        elif self.value == "http://www.w3.org/2004/02/skos/core#relatedMatch":
            return "~"
        elif self.value == "http://www.w3.org/2004/02/skos/core#narrowMatch":
            return ">"
        elif self.value == "http://www.w3.org/2004/02/skos/core#broadMatch":
            return "<"
        raise ValueError  # Just for silly type checking
