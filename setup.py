from setuptools import setup, find_packages

# не падаем, если нет requirements.txt
try:
    with open("requirements.txt") as f:
        install_requires = [l.strip() for l in f if l.strip()]
except FileNotFoundError:
    install_requires = []

# не импортируйте ваш пакет здесь!
VERSION = "0.0.2"

setup(
    name="protype_label_print",
    version=VERSION,
    description="Label printing for ERPNext (Item list action -> PDF)",
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
)
