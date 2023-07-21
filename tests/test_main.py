# #
# # MIT License
# #
# # (C) Copyright 2021-2023 Hewlett Packard Enterprise Development LP
# #
# # Permission is hereby granted, free of charge, to any person obtaining a
# # copy of this software and associated documentation files (the "Software"),
# # to deal in the Software without restriction, including without limitation
# # the rights to use, copy, modify, merge, publish, distribute, sublicense,
# # and/or sell copies of the Software, and to permit persons to whom the
# # Software is furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included
# # in all copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# # THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# # OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# # ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# # OTHER DEALINGS IN THE SOFTWARE.
# #
# """
# Unit tests for the product_deletion_utility.main module.
# """

# from argparse import Namespace
# import unittest
# from unittest.mock import patch


# from product_deletion_utility.main import (
#     main,
#     delete
# )
# from shasta_install_utility_common.products import ProductInstallException
# from shasta_install_utility_common.constants import (
#     DEFAULT_DOCKER_URL,
#     DEFAULT_NEXUS_URL,
#     PRODUCT_CATALOG_CONFIG_MAP_NAME,
#     PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE,
#     NEXUS_CREDENTIALS_SECRET_NAME,
#     NEXUS_CREDENTIALS_SECRET_NAMESPACE
# )


# class TestUninstall(unittest.TestCase):
#     """Tests for activate() and uninstall()."""
#     def setUp(self):
#         self.mock_product_catalog_cls = patch('product_deletion_utility.main.ProductCatalog').start()
#         self.mock_product_catalog = self.mock_product_catalog_cls.return_value

#         self.mock_product = self.mock_product_catalog.get_product.return_value
#         self.mock_product.product = 'old-product'
#         self.mock_product.version = 'x.y.z'
#         self.mock_product.clone_url = 'https://vcs.local/cray/product-deletion-config-management.git'

#     def tearDown(self):
#         """Stop patches."""
#         patch.stopall()

#     def test_uninstall_success(self):
#         """Test the successful case for uninstall()."""
#         delete(Namespace(
#             product=self.mock_product.product,
#             version=self.mock_product.version,
#             docker_url='mock_docker_url',
#             nexus_url='mock_nexus_url',
#             product_catalog_name='mock_name',
#             product_catalog_namespace='mock_namespace',
#             nexus_credentials_secret_name='mock_nexus_secret',
#             nexus_credentials_secret_namespace='mock_nexus_secret_namespace'
#         ))
#         self.mock_product_catalog_cls.assert_called_once_with(
#             name='mock_name',
#             namespace='mock_namespace',
#             docker_url='mock_docker_url',
#             nexus_url='mock_nexus_url',
#             nexus_credentials_secret_name='mock_nexus_secret',
#             nexus_credentials_secret_namespace='mock_nexus_secret_namespace'
#         )
#         self.mock_product_catalog.remove_product_docker_images.assert_called_once_with(self.mock_product.product, self.mock_product.version)
#         self.mock_product_catalog.uninstall_product_hosted_repos.assert_called_once_with(self.mock_product.product, self.mock_product.version)
#         self.mock_product_catalog.remove_product_entry.assert_called_once_with(self.mock_product.product, self.mock_product.version)


# class TestMain(unittest.TestCase):
#     def setUp(self):
#         """Set up mocks."""
#         self.mock_uninstall = patch('product_deletion_utility.main.delete').start()

#     def tearDown(self):
#         """Stop patches."""
#         patch.stopall()

#     def test_uninstall_action(self):
#         """Test a basic uninstall."""
#         action = 'uninstall'
#         product = 'old-product'
#         version = '2.0.3'
#         patch('sys.argv', ['product-deletion-utility', action, product, version]).start()
#         main()
#         self.mock_uninstall.assert_called_once_with(
#             Namespace(
#                 action=action,
#                 product=product,
#                 version=version,
#                 docker_url=DEFAULT_DOCKER_URL,
#                 nexus_url=DEFAULT_NEXUS_URL,
#                 product_catalog_name=PRODUCT_CATALOG_CONFIG_MAP_NAME,
#                 product_catalog_namespace=PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE,
#                 nexus_credentials_secret_name=NEXUS_CREDENTIALS_SECRET_NAME,
#                 nexus_credentials_secret_namespace=NEXUS_CREDENTIALS_SECRET_NAMESPACE,
#             )
#         )

#     def test_delete_action(self):
#         """Test a basic uninstall."""
#         action = 'delete'
#         product = 'old-product'
#         version = '2.0.3'
#         patch('sys.argv', ['product-deletion-utility', action, product, version]).start()
#         main()
#         self.mock_uninstall.assert_called_once_with(
#             Namespace(
#                 action=action,
#                 product=product,
#                 version=version,
#                 docker_url=DEFAULT_DOCKER_URL,
#                 nexus_url=DEFAULT_NEXUS_URL,
#                 product_catalog_name=PRODUCT_CATALOG_CONFIG_MAP_NAME,
#                 product_catalog_namespace=PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE,
#                 nexus_credentials_secret_name=NEXUS_CREDENTIALS_SECRET_NAME,
#                 nexus_credentials_secret_namespace=NEXUS_CREDENTIALS_SECRET_NAMESPACE
#             )
#         )

# if __name__ == '__main__':
#     unittest.main()
