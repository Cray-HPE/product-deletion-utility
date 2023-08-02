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
import copy
import unittest
from unittest.mock import call, Mock, patch
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

class TestDeleteProductComponent(unittest.TestCase):

    def setUp(self):
        """Set up mocks"""
        self.mock_delete_product_component= patch(product_deletion_utility.components.delete.DeleteProductComponent).start()
        self.mock_delete_product_component.get_product= Mock()
        self.mock_delete_product_component.mock_docker_api=Mock()
        self.mock_delete_product_component.mock_nexus_api=Mock()
        self.mock_delete_product_component.uninstall_component= Mock()
        self.mock_delete_product_component.uninstall_component.uninstall_docker_image=Mock()
        self.mock_delete_product_component.uninstall_component.uninstall_S3_artifact = Mock()
        self.mock_delete_product_component.uninstall_component.uninstall_helm_charts = Mock()
        self.mock_delete_product_component.uninstall_component.uninstall_loftsman_manifests = Mock()
        self.mock_delete_product_component.uninstall_component.uninstall_ims_recipes = Mock()
        self.mock_print = patch('builtins.print').start()
        
    def tearDown(self):
        """Stop patches."""
        patch.stopall()

    def test_remove_product_docker_images(self):
        """Test removing product docker images"""
        mock_product=Mock()
        mock_product.docker_images=[('image1', 'version1'), ('image2', 'version2')]

        self.mock_delete_product_component.get_product.return_value=mock_product

        self.mock_delete_product_component.remove_product_docker_images()

        self.mock_delete_product_component.uninstall_component.uninstall_docker_image.assert_any_call(
            'image1','version1', self.mock_delete_product_component.mock_docker_api
        )

        self.mock_delete_product_component.uninstall_component.uninstall_docker_image.assert_any_call(
            'image2','version2',self.mock_delete_product_component.mock_docker_api
        )

    def test_remove_product_docker_images_shared_image(self):
        """Test removing docker images shared by any other product"""
        mock_product= Mock()
        mock_product.docker_images=[('image1','version1')]
        self.mock_delete_product_component.get_product.return_value= mock_product

        mock_similar_product=Mock()
        mock_similar_product.docker_images=[('image1','version1')]
        self.mock_delete_product_component.products=[mock_similar_product]

        self.mock_delete_product_component.remove_product_docker_images()

        self.mock_delete_product_component.uninstall_component.uninstall_docker_image.assert_not_called()
        

if __name__ == '__main__':
    unittest.main()

