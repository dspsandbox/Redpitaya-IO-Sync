import os
import sys
import json
import sphinx.util.inspect as _sphinx_inspect
import sphinx.ext.autodoc as _autodoc
from sphinx.ext.autodoc import AttributeDocumenter

def _json_default(obj):
    if isinstance(obj, type):
        return obj.__name__
    if isinstance(obj, int):
        return hex(obj)
    return repr(obj)

_orig_object_description = _sphinx_inspect.object_description

def _object_description(obj):
    if isinstance(obj, dict):
        return "{...}"
    if isinstance(obj, list):
        return "[...]"
    return _orig_object_description(obj)

_sphinx_inspect.object_description = _object_description
_autodoc.object_description = _object_description

def _contains_types(obj):
    if isinstance(obj, type):
        return True
    if isinstance(obj, dict):
        return any(_contains_types(v) for v in list(obj.keys()) + list(obj.values()))
    if isinstance(obj, (list, tuple)):
        return any(_contains_types(v) for v in obj)
    return False

def _format_with_links(obj, indent=0):
    pad = "  " * indent
    inner = "  " * (indent + 1)
    if isinstance(obj, type):
        return f":class:`~{obj.__module__}.{obj.__name__}`"
    elif isinstance(obj, dict):
        if not obj:
            return "{}"
        parts = []
        items = list(obj.items())
        for i, (k, v) in enumerate(items):
            comma = "," if i < len(items) - 1 else ""
            parts.append(f'{inner}"{k}": {_format_with_links(v, indent + 1)}{comma}')
        return "{\n" + "\n".join(parts) + f"\n{pad}}}"
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        parts = []
        for i, v in enumerate(obj):
            comma = "," if i < len(obj) - 1 else ""
            parts.append(f"{inner}{_format_with_links(v, indent + 1)}{comma}")
        return "[\n" + "\n".join(parts) + f"\n{pad}]"
    elif isinstance(obj, int):
        return f'"{hex(obj)}"'
    else:
        return json.dumps(obj)

_orig_add_content = AttributeDocumenter.add_content

def _patched_add_content(self, more_content):
    _orig_add_content(self, more_content)
    try:
        obj = self.object
    except Exception:
        return
    if not isinstance(obj, (dict, list)):
        return
    src = self.get_sourcename()
    self.add_line("", src)
    if _contains_types(obj):
        formatted = _format_with_links(obj)
        self.add_line(".. parsed-literal::", src)
        self.add_line("", src)
        for line in formatted.splitlines():
            self.add_line("   " + line, src)
    else:
        formatted = json.dumps(obj, indent=2, default=_json_default)
        self.add_line(".. code-block:: json", src)
        self.add_line("", src)
        for line in formatted.splitlines():
            self.add_line("   " + line, src)
    self.add_line("", src)

AttributeDocumenter.add_content = _patched_add_content

sys.path.insert(0, os.path.abspath("../driver/src"))

project = "redpitaya-io-sync"
author = "Pau Gómez"
release = "0.1.1"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "myst_nb",
]

nb_execution_mode = "off"
suppress_warnings = ["myst.header", "myst.xref_missing"]

autodoc_mock_imports = ["zynq_tcp_ctrl"]
autodoc_member_order = "bysource"
autodoc_typehints = "description"

napoleon_google_docstring = True
napoleon_numpy_docstring = True

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable", None),
}

html_theme = "furo"
html_title = f"{project} {release}"

exclude_patterns = ["_build"]
