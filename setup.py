from setuptools import setup

setup(
    name='backend-core',
    version='0.1',
    description='juice backend core',
    author='geo.kim',
    author_email='geo.kim@juice.co.kr',
    include_package_data=True,
    install_requires=[
        'djangorestframework',
        'djangorestframework-simplejwt'
    ]
)
