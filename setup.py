import setuptools

setuptools.setup(
    name="tomotoio",
    version="0.0.1",
    url="http://github.com/tomoto/tomotoio",
    author="Tomoto S. Washio",
    author_email="tomoto@gmail.com",
    description="Playing with TOIO",
    packages=setuptools.find_packages(exclude=("examples")),
    install_requires=['bluepy >= 1.3.0']
)
