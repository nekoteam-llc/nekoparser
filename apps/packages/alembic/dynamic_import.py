import importlib
import os
import pkgutil
import sys


def import_subclasses(base_path):
    """
    Dynamically import all files from base_path
    """
    print("base_path", base_path)
    # Ensure base_path is absolute
    base_path = os.path.abspath(base_path)

    # Add the base_path to sys.path to ensure modules are found
    if base_path not in sys.path:
        sys.path.append(base_path)

    # Get the package name from base_path to correctly use relative imports
    base_package = os.path.basename(base_path)

    for loader, module_name, is_pkg in pkgutil.walk_packages([base_path]):
        # Construct the module name relative to the base package
        full_module_name = f"packages.{base_package}.{module_name}"

        try:
            # Import the module using its full name
            importlib.import_module(full_module_name)
        except Exception as e:
            print(f"Error importing module {full_module_name}: {e}")
