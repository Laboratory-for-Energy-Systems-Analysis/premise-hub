"""MCV-specific regenerated result tables."""

from ._source import ROOT, load

_results = load("results", ROOT=ROOT)


def __getattr__(name):
    return getattr(_results, name)
