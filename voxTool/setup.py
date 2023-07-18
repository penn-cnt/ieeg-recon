from setuptools import setup, find_packages

setup(
    name='voxtool',
    version='0.0.2',
    description='VoxTool: A tool for labeling intracranial electrodes on CT images',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/penn-cnt/ieeg-recon/',
    install_requires=['PyQt5','mayavi', 'pyface', 'pandas', 'matplotlib', 'nibabel', 'nilearn', 'pyyaml','scipy'],
    packages=['voxtool', 'voxtool.model', 'voxtool.view'],
    include_package_data=True,
    package_data={'voxtool': ["config.yml"]},
    entry_points={
        'console_scripts': [
            'voxtool = voxtool.launch_pyloc:main'
        ]
    },
)
