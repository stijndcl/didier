from didier.utils.types.string import leading


def test_leading():
    """Test leading() when it actually does something"""
    assert leading("0", "5") == "05"
    assert leading("0", "5", target_length=3) == "005"


def test_leading_not_necessary():
    """Test leading() when the input is already long enough"""
    assert leading("0", "05") == "05"


def test_leading_no_exact():
    """Test leading() when adding would bring you over the required length"""
    assert leading("ab", "c", target_length=6) == "abababc"


def test_leading_no_target_length():
    """Test leading() when target_length is None"""
    assert leading("0", "05", target_length=None) == "005"
