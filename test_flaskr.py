import os
import tempfile
import pytest

from scrubber import replace_phi


def test_replace_phi():
    text = "John went to the Mayo Clinic."

    phi_indices = [
        {
        "index_start": 0,
        "index_end": 4,
        "phi_type": "PERSON"
        },
        {
        "index_start": 13,
        "index_end": 28,
        "phi_type": "ORG"
        }
    ]

    deid = replace_phi(text, phi_indices)

    assert deid == '[*PERSON*] went to [*ORG*].'
