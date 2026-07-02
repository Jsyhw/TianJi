from flightvis.plotting.downsample import downsample_sequence, downsample_xyz


def test_downsample_leaves_small_sequence_unchanged():
    values = list(range(5))
    assert downsample_sequence(values, 10) is values


def test_downsample_caps_large_sequence_and_keeps_first():
    values = list(range(101))
    result = downsample_sequence(values, 10)
    assert len(result) <= 10
    assert result[0] == 0


def test_downsample_xyz_uses_same_step():
    x, y, z = downsample_xyz(list(range(20)), list(range(20, 40)), list(range(40, 60)), 7)
    assert len(x) == len(y) == len(z)
    assert x[0] == 0
    assert y[0] == 20
    assert z[0] == 40
