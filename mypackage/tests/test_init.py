from mypackage.core import add_two


def test_add_two():

    assert add_two(3) == 5


def test_add_two_list(fing):

    assert fing + 2 == add_two(fing)
