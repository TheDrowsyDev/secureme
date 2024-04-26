from common import call_securenv

'''
Tests related to the CLI program.
'''


def test_no_arguments():
    code, out = call_securenv("")
    assert code != 0
    assert 'error: the following arguments are required' in str(out)


def test_no_env_file():
    code, out = call_securenv("metadata")
    assert code != 0
    assert 'error: the following arguments are required' in str(out)
