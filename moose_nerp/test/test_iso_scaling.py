# -*- coding:utf-8 -*-

from moose_nerp.prototypes.iso_scaling import iso_scaling

def test_iso_scaling():
    assert iso_scaling([0]) == (u'', 1)
    assert iso_scaling([999]) == (u'', 1)
    assert iso_scaling([1000]) == (u'k', 1e3)
    assert iso_scaling([999999]) == (u'k', 1e3)
    assert iso_scaling([-1000]) == (u'k', 1e3)
    assert iso_scaling([-999999]) == (u'k', 1e3)
    assert iso_scaling([-1e-6]) == (u'µ', 1e-6)
