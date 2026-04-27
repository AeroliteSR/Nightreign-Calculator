from cx_Freeze import setup, Executable
import sys

include_files = [
    ("calc.ico", "calc.ico"),
    ("lacie.png", "lacie.png"),
    ("README.md", "README.md"),
    ("LICENSE", "LICENSE")
]

packages = ["Nightreign"]

build_exe_options = {
    "packages": packages,
    "include_files": include_files,
    "include_msvcr": True,
}

base = None
if sys.platform == "win32":
    base = "GUI"

setup(
    name="NRCalc",
    version="1.4.2",
    description="Nightreign Calculator",
    options={"build_exe": build_exe_options},
    executables=[Executable("NRCalc.py", base=base, icon="calc.ico")],
)