from setuptools import setup
import os

here = os.path.dirname(os.path.realpath(__file__))
HAS_CUDA = os.system("nvidia-smi > /dev/null 2>&1") == 0

VERSION = (
    "1.1.10"
    if "PKG_VERSION" not in os.environ or not os.environ["PKG_VERSION"]
    else os.environ["PKG_VERSION"]
)
DESCRIPTION = "HiQ - A Modern Observability System"

packages = ["hiq"]


def read_file(filename: str):
    try:
        lines = []
        with open(filename) as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines if not line.startswith("#")]
        return lines
    except:
        return []


def package_files(ds):
    paths = []
    for d in ds:
        for path, directories, filenames in os.walk(d):
            for filename in filenames:
                if "__pycache__" not in str(filename):
                    paths.append(str(os.path.join(path, filename))[len("src/hiq/") :])
    return paths


extra_files = package_files(["src/hiq/"])

r_fastapi = (read_file("requirements-fastapi.txt"),)
r_transformers = (read_file("requirements-transformers.txt"),)
r_lavis = (read_file("requirements-lavis.txt"),)
r_gpu = (read_file("requirements-gpu.txt"),)

setup(
    name="hiq-python",
    version=VERSION,
    author="Henry Fuheng Wu; Kathan Patel; Zixin Kong",
    author_email="<fuheng.wu@oracle.com>",
    description=DESCRIPTION,
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=read_file(f"{here}/requirements.txt"),
    keywords=[
        "hiq",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=packages,
    include_package_data=True,
    package_dir={"": "src"},
    package_data={"hiq": extra_files},
    url="https://github.com/oracle/hiq",
    extras_require={
        "fastapi": r_fastapi,
        "transformers": r_transformers,
        "lavis": r_lavis,
        "gpu": r_gpu,
        "full": r_fastapi + r_transformers + r_lavis + r_gpu,
    },
)
