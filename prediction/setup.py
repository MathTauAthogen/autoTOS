from distutils.command.sdist import sdist as sdist_orig
from distutils.errors import DistutilsExecError

from setuptools import setup, os

# os.system('sh install_finetune_and_spacy.sh')

setup(
    name="auto_tos_summarizer",
    version="0.2",
    scripts=["bin/install_finetune_and_spacy.sh", "predictor.py"],
    install_requires=[
        "tensorflow==2.2.0",
        "tensorflow-addons==0.10.0",
        "tensorflow-gpu",
    ],
)
