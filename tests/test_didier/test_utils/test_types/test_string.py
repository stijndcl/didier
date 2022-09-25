from didier.utils.types.string import abbreviate, leading, pluralize


def test_abbreviate_under_max_length():
    """Test abbreviate() when the input text is shorter than the max length"""
    text = "TEST STRING"
    assert abbreviate(text, max_length=len(text)) == text
    assert abbreviate(text, max_length=len(text) + 1) == text


def test_abbreviate_longer():
    """Test abbreviate() when the input text is longer than the max length"""
    text = "TEST STRING"
    assert abbreviate(text, max_length=7) == "TEST S…"


def test_abbreviate_whitespace():
    """Test abbreviate() when the max length would end on whitespace"""
    text = "TEST STRING"
    assert abbreviate(text, max_length=6) == "TEST…"


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


def test_pluralize_singular():
    """Test pluralize() when the word is singular"""
    word = "word"
    assert pluralize(word, amount=1, plural_form="whatever") == word


def test_pluralize_plural_default():
    """Test pluralize() for the default plural form (+s)"""
    word = "word"
    assert pluralize(word, amount=2) == "words"


def test_pluralize_custom_plural():
    """Test pluralize() when a custom plural form is provided"""
    word = "word"
    plural = "plural"
    assert pluralize(word, amount=2, plural_form=plural) == plural
