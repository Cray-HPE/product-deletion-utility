#
# MIT License
#
# (C) Copyright 2021-2023 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
"""
Contains common CLI arguments for install utility images.
"""

import argparse

from product_deletion_utility.components.constants import (
    NEXUS_CREDENTIALS_SECRET_NAME,
    NEXUS_CREDENTIALS_SECRET_NAMESPACE,
    DEFAULT_NEXUS_URL,
    DEFAULT_DOCKER_URL,
    PRODUCT_CATALOG_CONFIG_MAP_NAME,
    PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE,
    DEFAULT_LOG_DIR
)


def create_parser():
    """Create an argument parser for this command.

    Returns:
        argparse.ArgumentParser: The parser.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'action',
        choices=['delete', 'uninstall'],
        help='Specify the operation to execute on a product.'
    )

    parser.add_argument(
        'product',
        help='The name of the product to delete or activate.'
    )
    parser.add_argument(
        'version',
        help='Specify the version of the product to operate on.'
    )
    parser.add_argument(
        '--docker-url',
        help='Override the base URL of the Docker registry.',
        default=DEFAULT_DOCKER_URL,
    )
    parser.add_argument(
        '-d', '--dry-run',
        help='Lists the components that would be deleted for the provided product:version',
        default=False,
        type=lambda x: (str(x).lower() == 'true')
    )
    parser.add_argument(
        '--log-file',
        help='Log file name for file based logging.',
        default=DEFAULT_LOG_DIR,
    )

    product_catalog_group = parser.add_argument_group('product-catalog')
    product_catalog_group.add_argument(
        '--product-catalog-name',
        help='The name of the product catalog Kubernetes ConfigMap',
        default=PRODUCT_CATALOG_CONFIG_MAP_NAME
    )
    product_catalog_group.add_argument(
        '--product-catalog-namespace',
        help='The namespace of the product catalog Kubernetes ConfigMap',
        default=PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE
    )
    nexus_group = parser.add_argument_group('nexus')
    nexus_group.add_argument(
        '--nexus-url',
        help='Override the base URL of Nexus.',
        default=DEFAULT_NEXUS_URL
    )
    nexus_group.add_argument(
        '--nexus-credentials-secret-name',
        help='The name of the kubernetes secret containing HTTP authentication '
             'credentials for Nexus.',
        default=NEXUS_CREDENTIALS_SECRET_NAME,
    )
    nexus_group.add_argument(
        '--nexus-credentials-secret-namespace',
        help='The namespace of the kubernetes secret containing HTTP '
             'authentication credentials for Nexus.',
        default=NEXUS_CREDENTIALS_SECRET_NAMESPACE
    )

    return parser
