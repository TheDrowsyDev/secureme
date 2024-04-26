from common import create_test_app, verify_env_file
import sys
import pytest
import os
from pathlib import Path
from textual.pilot import Pilot
from textual.widgets import Input, ProgressBar
sys.path.append(str(Path(__file__).parent.parent))
from securenv.cli import SecureEnvScreen, DoneScreen, SecureEnvApp

'''
Tests related to the TUI.
'''

dir_path = os.path.dirname(os.path.realpath(__file__))

'''
1. Test trying to skip without entering anything
2. Test trying next with invalid entries
3. Test with valid entries
4. Test backwards navigation
5. Verify env file is created
'''


async def fill_in_username(app: SecureEnvApp, pilot: Pilot):
    input_area_container = app.get_widget_by_id("contentContainer")
    child_elems = input_area_container.children
    input_elems = [e for e in child_elems if isinstance(e, Input)]
    assert len(input_elems) > 0
    username_elem = input_elems[0]

    app.set_focus(username_elem)
    await pilot.press('u', 's', 'e', 'r', 'n', 'a', 'm', 'e')


async def fill_in_password(app: SecureEnvApp, pilot: Pilot):
    input_area_container = app.get_widget_by_id("contentContainer")
    child_elems = input_area_container.children
    input_elems = [e for e in child_elems if isinstance(e, Input)]
    assert len(input_elems) > 0
    password_elem = input_elems[1]

    app.set_focus(password_elem)
    await pilot.press("G", "o", "o", "d", "p", "a", "s", "s", "w", "o", "r", "d", "1", "2", "3", "!")


@pytest.mark.asyncio
async def test_empty_fields():
    app, variable_groups = create_test_app(pytest.env_file_name)

    default_min = 5
    var_group = variable_groups[0]['var_group']
    vars = var_group['vars']
    username_title = vars[0]['var']['name']
    username_complexity = vars[0]['var']['complexity']
    async with app.run_test() as pilot:
        assert isinstance(app.screen, SecureEnvScreen)
        await pilot.click(selector="#nextBtn")
        for elem in app._notifications:
            assert f"{username_title} must be between {default_min} and {username_complexity['max_length']}" in elem.message

        await pilot.exit(0)
    app.exit()


@pytest.mark.asyncio
async def test_valid_username():
    app, variable_groups = create_test_app(pytest.env_file_name)
    var_group = variable_groups[0]['var_group']
    vars = var_group['vars']
    password_title = vars[1]['var']['name']
    password_complexity = vars[1]['var']['complexity']
    async with app.run_test() as pilot:
        await fill_in_username(app, pilot)
        await pilot.click(selector="#nextBtn")
        for elem in app._notifications:
            assert f"{password_title} must be between {password_complexity['min_length']} and {password_complexity['max_length']}" in elem.message

        await pilot.exit(0)
    app.exit()


@pytest.mark.asyncio
async def test_invalid_numbers():
    app, variable_groups = create_test_app(pytest.env_file_name)

    var_group = variable_groups[0]['var_group']
    vars = var_group['vars']
    password_title = vars[1]['var']['name']
    password_complexity = vars[1]['var']['complexity']
    async with app.run_test() as pilot:
        # Fill in username
        await fill_in_username(app, pilot)

        # Long enough, but missing symbols, numbers, and uppercase
        input_area_container = app.get_widget_by_id("contentContainer")
        child_elems = input_area_container.children
        input_elems = [e for e in child_elems if isinstance(e, Input)]
        assert len(input_elems) > 0
        password_elem = input_elems[1]

        app.set_focus(password_elem)
        await pilot.press("g", "o", "o", "d", "p", "a", "s", "s", "w", "o", "r", "d")

        await pilot.click(selector="#nextBtn")
        for elem in app._notifications:
            assert f"{password_title} must have at least {password_complexity['numbers']} numbers in it" in elem.message


@pytest.mark.asyncio
async def test_invalid_symbols():
    app, variable_groups = create_test_app(pytest.env_file_name)

    var_group = variable_groups[0]['var_group']
    vars = var_group['vars']
    password_title = vars[1]['var']['name']
    password_complexity = vars[1]['var']['complexity']
    async with app.run_test() as pilot:
        # Fill in username
        await fill_in_username(app, pilot)

        # Long enough, but missing symbols, numbers, and uppercase
        input_area_container = app.get_widget_by_id("contentContainer")
        child_elems = input_area_container.children
        input_elems = [e for e in child_elems if isinstance(e, Input)]
        assert len(input_elems) > 0
        password_elem = input_elems[1]

        app.set_focus(password_elem)
        await pilot.press("g", "o", "o", "d", "p", "a", "s", "s", "w", "o", "r", "d", "1", "2", "3")

        await pilot.click(selector="#nextBtn")
        for elem in app._notifications:
            assert f"{password_title} must have at least {password_complexity['symbols']} symbols in it" in elem.message


@pytest.mark.asyncio
async def test_invalid_uppercase():
    app, variable_groups = create_test_app(pytest.env_file_name)

    var_group = variable_groups[0]['var_group']
    vars = var_group['vars']
    password_title = vars[1]['var']['name']
    password_complexity = vars[1]['var']['complexity']
    async with app.run_test() as pilot:
        # Fill in username
        await fill_in_username(app, pilot)

        # Long enough, but missing symbols, numbers, and uppercase
        input_area_container = app.get_widget_by_id("contentContainer")
        child_elems = input_area_container.children
        input_elems = [e for e in child_elems if isinstance(e, Input)]
        assert len(input_elems) > 0
        password_elem = input_elems[1]

        app.set_focus(password_elem)
        await pilot.press("g", "o", "o", "d", "p", "a", "s", "s", "w", "o", "r", "d", "1", "2", "3", "!")

        await pilot.click(selector="#nextBtn")
        for elem in app._notifications:
            assert f"{password_title} must have at least {password_complexity['uppercase']} uppercase letters in it" in elem.message


@pytest.mark.asyncio
async def test_valid_screen():
    app, _ = create_test_app(pytest.env_file_name)

    async with app.run_test() as pilot:
        # Fill in username
        await fill_in_username(app, pilot)

        # Long enough, but missing symbols, numbers, and uppercase
        input_area_container = app.get_widget_by_id("contentContainer")
        child_elems = input_area_container.children
        input_elems = [e for e in child_elems if isinstance(e, Input)]
        assert len(input_elems) > 0
        password_elem = input_elems[1]

        app.set_focus(password_elem)
        await pilot.press("G", "o", "o", "d", "p", "a", "s", "s", "w", "o", "r", "d", "1", "2", "3", "!")

        await pilot.click(selector="#nextBtn")
        assert len(app.screen_stack) == 3  # Should be a second screen now

        # Get the progress bar
        input_area_container = app.get_widget_by_id("contentContainer")
        child_elems = input_area_container.children
        progress_bars = [e for e in child_elems if isinstance(e, ProgressBar)]
        assert len(progress_bars) == 1
        assert progress_bars[0].percentage == 0.5


@pytest.mark.asyncio
async def test_prev_button():
    app, _ = create_test_app(pytest.env_file_name)

    async with app.run_test() as pilot:
        # Fill in username and password
        await fill_in_username(app, pilot)
        await fill_in_password(app, pilot)
        await pilot.click(selector="#nextBtn")
        assert len(app.screen_stack) == 3  # Should be a second screen now

        # Use prev button
        await pilot.click(selector="#prevBtn")
        input_area_container = app.get_widget_by_id("contentContainer")
        child_elems = input_area_container.children
        progress_bars = [e for e in child_elems if isinstance(e, ProgressBar)]
        assert len(progress_bars) == 1
        assert progress_bars[0].percentage == 0.0  # Assert progress goes back down


@pytest.mark.asyncio
async def test_env_file():
    app, variable_groups = create_test_app(pytest.env_file_name)

    async with app.run_test() as pilot:
        # Fill in username and password
        await fill_in_username(app, pilot)
        await fill_in_password(app, pilot)
        await pilot.click(selector="#nextBtn")
        assert len(app.screen_stack) == 3  # Should be a second screen now

        # Fill in second page
        await fill_in_username(app, pilot)
        await fill_in_password(app, pilot)
        await pilot.click(selector="#nextBtn")
        assert len(app.screen_stack) == 4  # Should be a second screen now
        assert isinstance(app.screen_stack[-1], DoneScreen)

        # Select done
        await pilot.click(selector="#exitBtn")

    # Check for env file
    assert os.path.exists(f"{dir_path}/../{pytest.env_file_name}")
    all_vars = []
    for elem in variable_groups:
        var_group = elem['var_group']
        vars = var_group['vars']
        for v in vars:
            name = v['var']['name']
            all_vars.append(name)
    assert verify_env_file(f"{dir_path}/../{pytest.env_file_name}", all_vars)
