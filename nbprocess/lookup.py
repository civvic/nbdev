# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/13_lookup.ipynb.

# %% auto 0
__all__ = ['nbprocess_lookup', 'NbdevLookup']

# %% ../nbs/13_lookup.ipynb 3
from .imports import *
from .read import *
from .export import *
from .doclinks import *
from fastcore.utils import *

import pkg_resources,importlib

if IN_NOTEBOOK:
    from IPython.display import Markdown,display
    from IPython.core import page
else: Markdown,display,page = None,None,None

# %% ../nbs/13_lookup.ipynb 5
class NbdevLookup:
    "Mapping from symbol names to URLs with docs"
    def __init__(self, strip_libs=None, incl_libs=None, skip_mods=None):
        skip_mods = setify(skip_mods)
        strip_libs = L(strip_libs)
        if incl_libs is not None: incl_libs = (L(incl_libs)+strip_libs).unique()
        # Dict from lib name to _nbprocess module for incl_libs (defaults to all)
        self.entries = {o.dist.key:o.load() for o in pkg_resources.iter_entry_points(group='nbdev')
                       if incl_libs is None or o.dist.key in incl_libs}
        py_syms = merge(*L(o.modidx['syms'].values() for o in self.entries.values()).concat())
        for m in strip_libs:
            _d = self.entries[m].modidx
            stripped = {remove_prefix(k,f"{mod}."):v
                        for mod,dets in _d['syms'].items() if mod not in skip_mods
                        for k,v in dets.items()}
            py_syms = merge(stripped, py_syms)
        self.syms = py_syms

    def __getitem__(self, s): return self.syms.get(s, None)

# %% ../nbs/13_lookup.ipynb 10
from ._nbdev import modidx
_settings = modidx['settings']
_strip_libs  = _settings.get('strip_libs',_settings.get('lib_name')).split()
nbprocess_lookup = NbdevLookup(_strip_libs)

# %% ../nbs/13_lookup.ipynb 14
@patch
def _link_sym(self:NbdevLookup, m):
    l = m.group(1)
    s = self[l]
    if s is None: return m.group(0)
    return rf"[{l}]({s})"

_re_backticks = re.compile(r'`([^`\s]+)`')
@patch
def _link_line(self:NbdevLookup, l): return _re_backticks.sub(self._link_sym, l)

@patch
def linkify(self:NbdevLookup, md):
    in_fence=False
    lines = md.splitlines()
    for i,l in enumerate(lines):
        if l.startswith("```"): in_fence=not in_fence
        elif not l.startswith('    ') and not in_fence: lines[i] = self._link_line(l)
    return '\n'.join(lines)