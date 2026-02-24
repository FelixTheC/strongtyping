from setuptools import Extension, setup

# Define the extension module
sttyping_module = Extension(
    "sttyping",
    sources=["src/sttypingmodule.c"],
    # Optional: add compiler flags for extra speed
    extra_compile_args=["-O3"],
)

setup(
    ext_modules=[sttyping_module],
)
