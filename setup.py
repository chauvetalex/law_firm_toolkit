from setuptools import setup
from setuptools import find_packages

# récupérer la liste des dépendances depuis requirements.txt
with open('requirements.txt') as f:
    content = f.readlines()
requirements = [line.strip() for line in content]

setup(name='law_firm_toolkit',
      version='0.1',
      description='Tools for law firms',
      url='',
      author='Alex CHAUVET',
      author_email='',
      license='MIT',
      packages=find_packages(),
      install_requires=requirements,
      zip_safe=False
    )
