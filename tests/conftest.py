import pytest
import os


def pytest_sessionstart(session: pytest.Session):
    pytest.env_file_name = "test_env.env"

    # Remove old file name if it exists
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if os.path.exists(f"{dir_path}/../{pytest.env_file_name}"):
        try:
            os.remove(f"{dir_path}/../{pytest.env_file_name}")
        except OSError as e:
            print(f"Error: Unable to remove old env file: {e}")
            os._exit(1)
