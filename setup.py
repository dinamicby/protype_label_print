from setuptools import setup, find_packages

setup(
    name="protype_label_print",
    version="0.0.2",
    description="Bulk label printing for Items on A4 with QR",
    author="Protype",
    app_description = "Bulk label printing for Items on A4 with QR"         
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    app_icon = "octicon octicon-tag",   # желательно
    app_color = "grey", 
    install_requires=[
        "qrcode[pil]==7.4.2"
    ]
)
