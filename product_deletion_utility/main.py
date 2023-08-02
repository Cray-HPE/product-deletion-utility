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
Entry point for the product deletion utility.
"""

import logging

from product_deletion_utility.components.delete import DeleteProductComponent, ProductInstallException
from product_deletion_utility.parser.parser import create_parser

def configure_logging():
    """Configure logging for the root logger.
    This sets up the root logger with the default format, WARNING log level, and
    stderr log handler.
    Returns:
        None.
    """
    CONSOLE_LOG_FORMAT = '%(levelname)s: %(message)s'
    logger = logging.getLogger()
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter(CONSOLE_LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.WARNING)


def delete(args):
    """Delete a version of a product.
    Args:
        args (argparse.Namespace): The CLI arguments to the command.
    Returns:
        None
    Raises:
        ProductInstallException: if uninstall failed.
    """
    delete_product_catalog = DeleteProductComponent(
        catalogname=args.product_catalog_name,
        catalognamespace=args.product_catalog_namespace,
        productname=args.product,
        productversion=args.version,
        nexus_url=args.nexus_url,
        docker_url=args.docker_url,
        nexus_credentials_secret_name=args.nexus_credentials_secret_name,
        nexus_credentials_secret_namespace=args.nexus_credentials_secret_namespace
    )

    delete_product_catalog.remove_product_docker_images()
    delete_product_catalog.remove_product_S3_artifacts()
    delete_product_catalog.remove_product_helm_charts()
    delete_product_catalog.remove_product_loftsman_manifests()
    delete_product_catalog.remove_ims_images()
    delete_product_catalog.remove_ims_recipes()
    delete_product_catalog.remove_product_hosted_repos()
    delete_product_catalog.remove_product_entry()


def main():
    """Main entry point.
    Returns:
        None
    Raises:
        SystemExit: if a ProductInstallException occurs.
    """
    configure_logging()
    parser = create_parser()
    args = parser.parse_args()
    try:
        if args.action == 'delete' or args.action == 'uninstall':
            delete(args)
    except ProductInstallException as err:
        print(err)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
