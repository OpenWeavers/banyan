from setuptools import setup

setup(
    name='banyan',
    version='1',
    packages=['Banyan'],
    url='https://openweavers.github.io/banyan/',
    license='GPLv3',
    author='Vinyas N S, Vinayaka K V, Monish S R',
    author_email='vinyasns@gmail.com',
    description='A simple P2P application protocol',
    entry_points={
        'console_scripts': [
            'banyan=Banyan.BanyanCLI:main',
        ],
    },
)
