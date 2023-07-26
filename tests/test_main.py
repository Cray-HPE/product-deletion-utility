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
        self.mock_Uninstall_Components= UninstallComponents()
        self.mock_docker_api= Mock()
        self.mock_nexus_api= Mock()
        self.mock_UninstallComponents.uninstall_docker_image= Mock()
        self.mock_UninstallComponents.uninstall_s3_artifacts= Mock()
        self.mock_UninstallComponents.uninstall_hosted_repos= Mock()
        self.mock_UninstallComponents.uninstall_helm_charts= Mock()
        self.mock_UninstallComponents.uninstall_loftsman_manifests= Mock()
        self.mock_UninstallComponents.uninstall_ims_recipies= Mock()
        self.mock_UninstallComponents.uninstall_ims_images= Mock()
        self.mock_docker_api.delete_image= Mock()
        self.mock_subprocess.checkoutput= Mock()
        self.mock_nexus_api.repos.delete= Mock()
        self.mock_nexus_api.components.delete= Mock()
        self.mock_print = patch('builtins.print').start()
	      
    def tearDown(self):
        """Stop patches."""
        patch.stopall()	

    def test_uninstall_docker_image(self):
	
        self.mock_UninstallComponents.uninstall_docker_image('image1', 'version1', self.mock_docker_api)
        self.mock_docker_api.delete_image.assert_called_once_with('image1', 'version1')
			
    def test_uninstall_docker_image_err(self):
	
        self.mock_docker_api.delete_image.side_effect= ProductInstallException(
        "Error occurred")
		
        with self.assertRaises(ProductInstallException):
            self.mock_UninstallComponents.uninstall_docker_image('image1', 'version1', self.mock_docker_api)
		
        self.mock_docker_api.delete_image.assert_called_once_with('image1', 'version1')
		
        self.mock_print.assert_called_once_with(
            "Failed to remove image image1:version1: Error occured")
		
    def test_uninstall_s3_artifacts(self):
		
        self.mock_UninstallComponents.uninstall_s3_artifacts('bucket1', 'key1')
        self.mock_subprocess.check_output.assert_called_once_with('bucket1', 'key1')
		
    def test_uninstall_s3_artifacts_err(self):
	
        self.mock_subprocess.check_output.side_effect= ProductInstallException(
        "Error occurred")
	    	
        with self.assertRaises(ProductInstallException):
            self.mock_UninstallComponents.uninstall_s3_artifacts('bucket1', 'key1')
	
        self.mock_subprocess.check_output.assert_called_once_with('bucket1', 'key1')
        self.mock_print.assert_called_once_with("Failed to remove bucket1:key1 from S3 artifacts")
		
    def test_uninstall_hosted_repos(self):

        self.mock_UninstallComponents.uninstall_hosted_repos('repo1', self.mock_nexus_api)
        self.mock_nexus_api.repos.delete.assert_called_once_with('repo1')
	
    def test_uninstall_hosted_repos_err(self):
	
        self.mock_nexus_api.repos.delete.side_effect = ProductInstallException(
        "Error occurred" )
	
        with self.assertRaises(ProductInstallException):
            self.mock_UninstallComponents.uninstall_hosted_repos('repo1', self.mock_nexus_api)
	
        self.mock_print.assert_called_once_with("Failed to remove repository repo1")
		
    def test_uninstall_helm_charts(self):
	
        self.mock_UninstallComponents.uninstall_helm_charts('chart1', 'version1', 'nexus_id', mock_nexus_api)
        self.mock_nexus_api.components.delete.assert_called_once_with('nexus_id')
	
    def test_uninstall_helm_charts_err(self):
	
        self.mock_nexus_api.components.delete.side_effect=ProductInstallException(
        "Error occurred" )
	   
        with self.assertRaises(ProductInstallException):
            self.mock_UninstallComponents.uninstall_helm_charts('chart1', 'version1', 'nexus_id', mock_nexus_api)
	
        self.mock_print.assert_called_once_with("Failed to remove helm chart chart1 ")
	
    def test_uninstall_loftsman_manifests(self):
	
        mock_manifest_keys = [ 'manifest1', 'manifest2']
	
        self.mock_UninstallComponents.uninstall_loftsman_manifests(mock_manifest_keys)
        self.mock_subprocess.check_output.assert_any_call('manifest1')
        self.mock_subprocess.check_output.assert_any_call('manifest2')
	
    def test_uninstall_loftsman_manifests_err(self):
		
        mock_manifest_keys = [ 'manifest1', 'manifest2']
		
        self.mock_subprocess.check_output.side_effect = ProductInstallException(
         "Error occurred" )
	
        with self.assertRaises(ProductInstallException) as context:
            self.mock_UninstallComponents.uninstall_loftsman_manifests(mock_manifest_keys)
	
        self.mock_print.assert_called_once_with("Failed to remove loftsman manifest manifest_keys from S3")
		
    def test_uninstall_ims_recipies(self):
		
        mock_command ='cmd1'
        mock_s3_key = 'key1'
        mock_s3_cmd = 'cmd_s3'
        mock_ims_cmd = 'cmd_ims'
	
        self.mock_UninstallComponents.uninstall_ims_recipies('recipe1', 'recipe_id1')
		
        self.mock_subprocess.check_output.assert_called_once_with('cmd1')
        self.mock_subprocess.check_output.assert_called_once_with('cmd_s3')
        self.mock_subprocess.check_output.assert_called_once_with('cmd_ims')
	
    def test_uninstall_ims_recipies_err(self):
	
        self.mock_subprocess.check_output.side_effect = ProductInstallException(
        "Error occurred")

        with self.assertRaises(ProductInstallException) as context:
            self.mock_UninstallComponents.uninstall_ims_recipies('recipe1', 'recipe_id1')
	
        self.mock_print.assert_called_once_with("Failed to remove IMS recipe 'recipe1' ")

    def test_uninstall_ims_images(self):

        mock_command ='cmd1'
        mock_s3_key = 'key1'
        mock_s3_cmd = 'cmd_s3'
        mock_ims_cmd = 'cmd_ims'

        self.mock_UninstallComponents.uninstall_ims_images('image1', 'image_id1')

        self.mock_subprocess.check_output.assert_called_once_with('cmd1')
        self.mock_subprocess.check_output.assert_called_once_with('cmd_s3')
        self.mock_subprocess.check_output.assert_called_once_with('cmd_ims')

    def test_uninstall_ims_images_err(self):

        self.mock_suprocess.check_output.side_effect = ProductInstallException(
         "Error occurred" )

        with self.assertRaises(ProductInstallException) as context:
            self.mock_UninstallComponents.uninstall_ims_recipies('image1', 'image_id1')

        self.mock_print.assert_called_once_with("Failed to remove IMS image image1")

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

