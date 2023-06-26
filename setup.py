from setuptools import setup, find_packages

setup(
    name='ultronai_cdn_tools',
    version='0.1.0',
    author='Anudeepsekhar Bolimera',
    author_email='anudeep.sekhar@gmail.com',
    description='Ultron AI CDN tools package',
    packages=find_packages(),
    install_requires=[
        'azure-storage-blob',
        'python-dotenv',
        'datetime'
    ],
)