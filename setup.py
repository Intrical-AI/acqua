"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='Acqua',
    version='0.0.13',
    description='A flow based library to precompute analytics',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Intrical-AI/acqua',
    author='Intrical AI',
    author_email='alvise.sembenico@intrical.ai',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent'
    ],

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    # package_dir={'': 'src'},  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages(),
    python_requires='>=3.6, <4',
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['appdirs==1.4.3',
                      'argon2-cffi==20.1.0',
                      'async-generator==1.10',
                      'attrs==20.3.0',
                      'autopep8==1.5.6',
                      'backcall==0.2.0',
                      'bleach==3.3.0',
                      'boto3==1.17.33',
                      'botocore==1.20.33',
                      'build==0.3.1.post1',
                      'CacheControl==0.12.6',
                      'certifi==2019.11.28',
                      'cffi==1.14.5',
                      'chardet==3.0.4',
                      'colorama==0.4.3',
                      'contextlib2==0.6.0',
                      'cryptography==3.4.6',
                      'decorator==4.4.2',
                      'defusedxml==0.7.1',
                      'distlib==0.3.0',
                      'distro==1.4.0',
                      'dnspython==1.16.0',
                      'docutils==0.16',
                      'elasticsearch==7.11.0',
                      'elasticsearch-dsl==7.3.0',
                      'entrypoints==0.3',
                      'frozendict==1.2',
                      'greenlet==1.0.0',
                      'html5lib==1.0.1',
                      'idna==2.8',
                      'importlib-metadata==3.7.3',
                      'ipywidgets==7.6.3',
                      'jeepney==0.6.0',
                      'Jinja2==2.11.3',
                      'jmespath==0.10.0',
                      'jsonschema==3.2.0',
                      'keyring==23.0.0',
                      'lockfile==0.12.2',
                      'MarkupSafe==1.1.1',
                      'mistune==0.8.4',
                      'msgpack==0.6.2',
                      'nbclient==0.5.3',
                      'nbconvert==6.0.7',
                      'nbformat==5.1.2',
                      'nest-asyncio==1.5.1',
                      'notebook==6.2.0',
                      'packaging==20.3',
                      'pandocfilters==1.4.3',
                      'parso==0.8.1',
                      'pep517==0.10.0',
                      'pexpect==4.8.0',
                      'pickleshare==0.7.5',
                      'pkginfo==1.7.0',
                      'progress==1.5',
                      'prometheus-client==0.9.0',
                      'prompt-toolkit==3.0.17',
                      'psycopg2-binary==2.8.6',
                      'ptyprocess==0.7.0',
                      'pycodestyle==2.7.0',
                      'pycparser==2.20',
                      'Pygments==2.8.1',
                      'pymongo==3.11.3',
                      'pyparsing==2.4.6',
                      'pyrsistent==0.17.3',
                      'python-dateutil==2.8.1',
                      'python-dotenv==0.15.0',
                      'pytoml==0.1.21',
                      'pyzmq==22.0.3',
                      'qtconsole==5.0.3',
                      'QtPy==1.9.0',
                      'readme-renderer==29.0',
                      'requests==2.22.0',
                      'requests-toolbelt==0.9.1',
                      'retrying==1.3.3',
                      'rfc3986==1.4.0',
                      'Rx==3.1.1',
                      's3transfer==0.3.6',
                      'SecretStorage==3.3.1',
                      'Send2Trash==1.5.0',
                      'simple-settings==1.0.0',
                      'six==1.14.0',
                      'SQLAlchemy==1.4.2',
                      'terminado==0.9.3',
                      'testpath==0.4.4',
                      'toml==0.10.2',
                      'tornado==6.1',
                      'tqdm==4.59.0',
                      'traitlets==5.0.5',
                      'twine==3.4.1',
                      'urllib3==1.25.8',
                      'wcwidth==0.2.5',
                      'webencodings==0.5.1',
                      'widgetsnbextension==3.5.1',
                      'zipp==3.4.1', ],

    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/Intrical-AI/acqua/issues',
        'Source': 'https://github.com/Intrical-AI/acqua/',
    },
)
