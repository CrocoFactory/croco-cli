"""
Class for making options to be shown on screen during KeyMode
"""
from typing import Any
from dataclasses import dataclass
from .types import AnyCallable


@dataclass(frozen=True)
class Option:
    """
    Class for making options to be shown on screen during KeyMode

    :param name: Name of the option
    :param description: Description of the option
    :param handler: Action to be performed on this option
    :param deleting_handler: Action to be performed on the deleting of this option
    """

    name: str
    handler: AnyCallable
    description: str | None = None
    deleting_handler: AnyCallable = lambda: None

    def get(self, attr: str, default: Any = None) -> Any:
        """
        Gets an attribute in option
        :param attr: Attribute name
        :param default: Default value to be returned if the attribute is not found.
        :return: The attribute value or default value if the attribute is not found.
        """
        return res if (res := getattr(self, attr)) else default
