import os

pkg_name = input(
    'Enter your desired package name (separated by hyphens (-)): ')
script_name = input(
    'Enter your desired cli tool name (once again, separated by hyphens), leave blank if no associated cli tool: ')

pkg_name_underscores = pkg_name.replace('-', '_')

os.system(f"sed -i 's/package-boilerplate/{pkg_name}/g' setup.py")
os.system(f"mv package_boilerplate {pkg_name_underscores}")

if script_name:
    # set scripts line to script_name
    os.system(f"sed -i 's/boilerplate-cli/{script_name}/g' setup.py")

    # set filename to match
    os.system(f"cd scripts && mv boilerplate-cli {script_name}")

    # set script to read
    os.system(
        f"cd scripts && sed -i 's/package_boilerplate/{pkg_name_underscores}/g' {script_name}")
else:
    # delete scripts line
    os.system("sed -i '/scripts=/ d' setup.py")

    # delete scripts directory
    os.system("rm -r scripts")
