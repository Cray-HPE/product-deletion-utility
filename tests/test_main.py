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
import unittest
from unittest.mock import patch
from nexusctl import DockerApi

from product_deletion_utility.main import (
    main,
    delete
)

from product_deletion_utility.components.delete import (
     UninstallComponents,
     DeleteProductComponent,ProductInstallException
)

from product_deletion_utility.components.constants import (
    DEFAULT_DOCKER_URL,
    DEFAULT_NEXUS_URL,
    NEXUS_CREDENTIALS_SECRET_NAME,
    NEXUS_CREDENTIALS_SECRET_NAMESPACE,
    PRODUCT_CATALOG_CONFIG_MAP_NAME,
    PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE
)
 
class TestUninstallComponents(unittest.TestCase):
    """Tests for UninstallComponents."""

    def setup(self):
        """Set up mocks"""
        mock_UninstallComponents= patch('product_deletion_utility.components.delete.UninstallComponents').start()
        mock_docker_api= patch('nexusctl.DockerApi').start()
        mock_docker_api.list_repos=Mock()
        
	      
    def tearDown(self):
        """Stop patches."""
        patch.stopall()	

    def test_uninstall_docker_image(self):
        mock_UninstallComponents.uninstall_docker_image('image1', 'version1', self.mock_docker_api)
        mock_UninstallComponents.uninstall_docker_image.assert_called_once_with('image1', 'version1', self.mock_docker_api)
	    
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

