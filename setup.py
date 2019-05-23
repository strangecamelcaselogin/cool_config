from setuptools import setup, find_packages


with open('README.md') as f:
    long_description = f.read()


setup(name='cool_config',
      version='0.2.3',
      long_description=long_description,
      long_description_content_type='text/markdown',
      description='Another Python configuration tool',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
      ],
      url='https://github.com/strangecamelcaselogin/cool_config',
      author='strangecamelcaselogin',
      author_email='strangecamelcaselogin@gmail.com',
      license='MIT',
      packages=find_packages(),
      python_requires='>=3.6',
      install_requires=[
          'pyyaml>=4.2b1'
      ],
      include_package_data=True,
      zip_safe=False)
