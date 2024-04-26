from common import call_securenv
import os

'''
Tests related to the CLI program.
'''

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_nonexistent_metadata_file():
    code, out = call_securenv("./data/nonexistent.yaml", ".env")
    assert code != 0
    assert "Unable to find file" in str(out)


def test_bad_metadata_file():
    code, out = call_securenv(f"{dir_path}/data/test.txt", ".env")
    assert code != 0
    assert "Metadata format is invalid" in str(out)


def test_invalid_metadata_file():
    code, out = call_securenv(f"{dir_path}/data/test_invalid_metadata.yaml",
                              ".env")
    assert code != 0
    assert "Metadata format is invalid" in str(out)
