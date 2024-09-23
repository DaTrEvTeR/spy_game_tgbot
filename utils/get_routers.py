from aiogram import Router

import routers
from utils.find_attributes_recursively import find_attributes


def get_routers() -> list[Router]:
    """This function retrieves all instances of `Router` defined in any module named "routes"
    within the `src` package and its subpackages.

    Returns:
    -------
    list[Router]
        A list of `Router` instances found in the "routes" modules across the routers package.
    """
    return list(
        find_attributes(
            module=routers,
            attribute_type=Router,
            match_module_name="routes",
        ).values(),
    )
