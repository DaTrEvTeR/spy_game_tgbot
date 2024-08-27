import pkgutil
from importlib.machinery import FileFinder
from types import ModuleType
from typing import Any, Dict


def find_attributes_recursively(
    module: ModuleType,
    attribute_name: str | None = None,
    attribute_type: type | None = None,
    match_module_name: str | None = None,
) -> Dict[int, Any]:
    """Recursively searches through a module and its submodules to find global attributes
    based on their name and/or type.

    :param module: The root module from which the search will begin.
    :type module: ModuleType
    :param attribute_name: The specific name of the attribute to find. If None, finds all attributes.
    :type attribute_name: str | None
    :param attribute_type: The type of the attribute to find. If None, finds all types.
    :type attribute_type: type | None
    :param match_module_name: A specific module name to search within. If None, searches all submodules.
    :type match_module_name: str | None
    :return: A dictionary where the keys are unique IDs of the found attributes,
    and the values are the attributes themselves.
    :rtype: Dict[int, Any]
    """
    attributes: Dict[int, Any] = {}
    for loader, module_name, is_pkg in pkgutil.walk_packages(module.__path__):
        if isinstance(loader, FileFinder):
            module_spec = loader.find_spec(module_name)
            if module_spec and module_spec.loader:
                if is_pkg:
                    submodule = module_spec.loader.load_module(module_name)
                    attributes.update(
                        find_attributes_recursively(submodule, attribute_name, attribute_type, match_module_name),
                    )
                elif not match_module_name or module_name == match_module_name:
                    submodule = module_spec.loader.load_module(module_name)
                    for global_attr_name in dir(submodule):
                        if attribute_name and attribute_name != global_attr_name:
                            continue
                        global_attr = getattr(submodule, global_attr_name)
                        if global_attr and id(global_attr) not in attributes:
                            if attribute_type and not isinstance(global_attr, attribute_type):
                                continue
                            attributes[id(global_attr)] = global_attr
    return attributes
