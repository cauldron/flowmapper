class DifferingMatches(Exception):
    """Multiple different matches given for same flow"""


class DifferingConversions(Exception):
    """Multiple, different conversion factors provided for a given match"""


class MissingLocation(Exception):
    """Expected a location element in a name, but didn't find any"""
