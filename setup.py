import json
from setuptools import setup

with open('package.json') as f:
    package = json.load(f)

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

package_name = package['name'].replace(' ', '_').replace('-', '_')

setup(
    name=package_name,
    version=package['version'],
    author=package['author'],
    packages=[package_name],
    include_package_data=True,
    license=package['license'],
    description=package.get('description', package_name),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pip-install-python/dash-mui-scheduler',
    project_urls={
        'Bug Reports': 'https://github.com/pip-install-python/dash-mui-scheduler/issues',
        'Source': 'https://github.com/pip-install-python/dash-mui-scheduler',
        'Documentation': 'https://muischeduler.2plot.dev',
    },
    install_requires=['dash>=2.11.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Dash',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: User Interfaces',
    ],
    keywords='dash plotly scheduler calendar timeline mui material-ui events',
    python_requires='>=3.8',
)
