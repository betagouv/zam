from dataclasses import fields
from sqlalchemy import inspect

import pytest

from zam_repondeur.models import Amendement


@pytest.mark.parametrize("name", [field.name for field in fields(Amendement)])
def test_amendement_field_is_mapped(name):
    insp = inspect(Amendement)
    mapped_cols = [c_attr.key for c_attr in insp.mapper.column_attrs]
    assert name in mapped_cols
