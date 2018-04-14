from setuptools import setup

setup(
    name='banyancli',
    version='1.2',
    packages=['banyancli'],
    url='https://openweavers.github.io/banyan/',
    license='GPLv3',
    author='Vinyas N S, Vinayaka K V, Monish S R',
    author_email='vinyasns@gmail.com',
    description='A simple P2P application protocol',
    entry_points={
        'console_scripts': [
            'banyan=banyancli.BanyanCLI:main',
        ],
    },
)
