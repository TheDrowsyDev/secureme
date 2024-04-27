# Securenv

![SecurEnv](https://github.com/TheDrowsyDev/securenv/raw/main/assets/logo-transparent.png?raw=true)

</br>
</br>

---

[![Linting](https://github.com/TheDrowsyDev/securenv/actions/workflows/linting.yaml/badge.svg)](https://github.com/TheDrowsyDev/securenv/actions/workflows/linting.yaml)
[![Tests](https://github.com/TheDrowsyDev/securenv/actions/workflows/test_suite.yaml/badge.svg)](https://github.com/TheDrowsyDev/securenv/actions/workflows/test_suite.yaml)

### Overview

Seucrenv is a TUI-based application for securely setting environment variables in a constrained fashion. Instead of setting default passwords in env files or hoping that users set *good* passwords, Securenv allows you to define complexity requirements for ENV variables before your application is even started!

### Installation

You can install Securenv via pip:
```
pip install securenv
```

After installation, you should now have a command `securenv`.

### Metadata File

To run `securenv`, you'll need to define a metadata file that defines the ENV variables to set, and their respective attributes such as sensitivity and complexity.
Below is an example metadata file:
```
- var_group:
    title: OpenSearch Application Variables
    vars:
      - var:
          name: OPENSEARCH_USERNAME
          placeholder: "admin"
          sensitive: false
          complexity:
            max_length: 15
      - var:
          name: OPENSEARCH_PASSWORD
          sensitive: true
          placeholder: "password"
          complexity:
            max_length: 20
            min_length: 10
            numbers: 3
            symbols: 1
            uppercase: 1
- var_group:
    title: Redis Variables
    vars:
    - var:
        name: REDIS_USERNAME
        placeholder: "admin"
        sensitive: false
        complexity:
            max_length: 15
    - var:
        name: REDIS_PASSWORD
        sensitive: true
        placeholder: "password"
        complexity:
            max_length: 20
            min_length: 10
- var_group:
    title: MLFlow Variables
    vars:
    - var:
        name: MLFLOW_USERNAME
        placeholder: "admin"
        sensitive: false
        complexity:
            max_length: 15
    - var:
        name: MLFLOW_PASSWORD
        sensitive: true
        placeholder: "password"
        complexity:
            max_length: 20
            min_length: 10
```

The required metadata file needs to be a valid YAML list of `var_group`'s. A `var_group` in Securenv is simply a grouping of related enviornment variables, typically a username and password for a single application. Each of these groups *must* have a `title` key and at least one `var` key. The `title` representing the name of the var group, i.e., `MLFLow Variables`.

Each `var` needs to conform to the following schema:
| Key | Description | Type | Required |
| ----------- | ----------- | ----------- | ----------- |
| name | Variable Name | str | True |
| sensitive | Whether the variable should be obfuscated during runtime | bool | True |
| placeholder | Placeholder in Input Widget for variable | str | True |
| complexity | Complexity requirements for variable | dict | False |
| max_length | Maximum length for variable | int | False |
| min_length | Minimum length for variable | int | False |
| numbers | Minimum required digits for variable | int | False |
| symbols | Minimum required symbols for variable | int | False |
| uppercase | Minimum required uppercase letters for variable | int | False |

This metadata schema will be checked at runtime for errors.

### Running

With a metadata file defined, simply run Securenv like so:
```
securenv metadata.yaml .env
```

After filling out all the variables according to the defined requirements, the env file that is specified will either be updated or created with the defined environment variables!

### Contributing

This is a small project created by one developer. Please feel free to submit feature request or report issues, and I'll do my best to implement them. Open to open-source contributions as well!