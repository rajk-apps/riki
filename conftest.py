def pytest_addoption(parser):
    parser.addoption("--large", action="store_true", help="run large tests")


def pytest_generate_tests(metafunc):

    if "fing" in metafunc.fixturenames:

        fing = [1, 2, 5, 10]

        if metafunc.config.getoption("large"):
            fing += [50, 100]

        metafunc.parametrize("fing", fing)
