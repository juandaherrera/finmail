"""Project related functions."""

import toml


def get_version_from_toml(config_path: str = "pyproject.toml") -> str:
    """
    Get the version from the project configuration file.

    Parameters
    ----------
    config_path : str, optional
        Path of the configuration, by default "pyproject.toml"

    Returns
    -------
    str
        Version of the project.
    """
    with open(config_path, encoding="utf-8") as file:
        config = toml.load(file)
    return config["project"]["version"]
