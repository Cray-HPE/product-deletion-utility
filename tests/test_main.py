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
Unit tests for the product_deletion_utility.main module.
"""

from argparse import Namespace
import subprocess
import unittest
from unittest.mock import patch, Mock

from urllib.error import HTTPError

from cray_product_catalog.query import  ProductInstallException

from product_deletion_utility.main import (
    main,
    delete
)



from product_deletion_utility.components.delete import (
    PRODUCT_CATALOG_CONFIG_MAP_NAME,
    PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE,
    UninstallComponents,
    DeleteProductComponent
)


from product_deletion_utility.components.constants import (
    DEFAULT_DOCKER_URL,
    DEFAULT_NEXUS_URL,
    NEXUS_CREDENTIALS_SECRET_NAME,
    NEXUS_CREDENTIALS_SECRET_NAMESPACE
)
 


class TestDelete(unittest.TestCase):
    """Tests for delete()."""
    def setUp(self):
        self.mock_product_catalog_cls = patch('product_deletion_utility.main.DeleteProductComponent').start()
        self.mock_product_catalog = self.mock_product_catalog_cls.return_value

        self.mock_product = self.mock_product_catalog.get_product.return_value
        self.mock_product.product = 'old-product'
        self.mock_product.version = 'x.y.z'
        self.mock_product.clone_url = 'https://vcs.local/cray/product-deletion-config-management.git'

    def tearDown(self):
        """Stop patches."""
        patch.stopall()

    def test_delete_success(self):
        """Test the successful case for uninstall()."""
        delete(Namespace(
            catalogname='mock_name',
            catalognamespace='mock_namespace',
            productname=self.mock_product.product,
            productversion=self.mock_product.version,
            nexus_url='mock_nexus_url',
            docker_url='mock_docker_url',
            nexus_credentials_secret_name='mock_nexus_secret',
            nexus_credentials_secret_namespace='mock_nexus_secret_namespace'
        ))
        self.mock_product_catalog_cls.assert_called_once_with(
            name='mock_name',
            namespace='mock_namespace',
            docker_url='mock_docker_url',
            nexus_url='mock_nexus_url',
            nexus_credentials_secret_name='mock_nexus_secret',
            nexus_credentials_secret_namespace='mock_nexus_secret_namespace'
        )
        self.mock_product_catalog.remove_product_docker_images.assert_called_once()
        self.mock_product_catalog.remove_product_S3_artifacts.assert_called_once()
        self.mock_product_catalog.remove_product_helm_charts.assert_called_once()
        self.mock_product_catalog.remove_product_loftsman_manifests.assert_called_once()
        self.mock_product_catalog.remove_ims_recipes.assert_called_once()
        self.mock_product_catalog.remove_ims_images.assert_called_once()
        self.mock_product_catalog.uninstall_product_hosted_repos.assert_called_once()
        self.mock_product_catalog.remove_product_entry.assert_called_once()

class TestMain(unittest.TestCase):
    def setUp(self):
        """Set up mocks."""
        self.mock_delete = patch('product_deletion_utility.main.delete').start()

    def tearDown(self):
        """Stop patches."""
        patch.stopall()

    def test_delete_action(self):
        """Test a basic delete."""
        action = 'delete'
        product = 'old-product'
        version = '2.0.3'
        patch('sys.argv', ['product-deletion-utility', action, product, version]).start()
        main()
        self.mock_delete.assert_called_once_with(
            Namespace(
                action=action,
                product=product,
                version=version,
                docker_url=DEFAULT_DOCKER_URL,
                nexus_url=DEFAULT_NEXUS_URL,
                product_catalog_name=PRODUCT_CATALOG_CONFIG_MAP_NAME,
                product_catalog_namespace=PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE,
                nexus_credentials_secret_name=NEXUS_CREDENTIALS_SECRET_NAME,
                nexus_credentials_secret_namespace=NEXUS_CREDENTIALS_SECRET_NAMESPACE
            )
        )


if __name__ == '__main__':
    unittest.main()
