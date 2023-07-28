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

class TestUninstallComponents(unittest.TestCase):
    """Tests for UninstallComponents."""

    def setUp(self):
        """Set up mocks"""
        self.mock_UninstallComponents= UninstallComponents()
        self.mock_UninstallComponents.mock_docker_api= Mock()
        self.mock_UninstallComponents.mock_nexus_api= Mock()
        self.mock_UninstallComponents.uninstall_docker_image= Mock()
        self.mock_UninstallComponents.uninstall_s3_artifacts= Mock()
        self.mock_UninstallComponents.uninstall_hosted_repos= Mock()
        self.mock_UninstallComponents.uninstall_helm_charts= Mock()
        self.mock_UninstallComponents.uninstall_loftsman_manifests= Mock()
        self.mock_UninstallComponents.uninstall_ims_recipies= Mock()
        self.mock_UninstallComponents.uninstall_ims_images= Mock()
        self.mock_UninstallComponents.mock_subprocess= Mock()
        self.mock_UninstallComponents.mock_docker_api.delete_image= Mock()
        self.mock_UninstallComponents.mock_subprocess.checkoutput= Mock()
        self.mock_UninstallComponents.mock_nexus_api.repos.delete= Mock()
        self.mock_UninstallComponents.mock_nexus_api.components.delete= Mock()
        self.mock_print = patch('builtins.print').start()
	      
    def tearDown(self):
        """Stop patches."""
        patch.stopall()	

    def test_uninstall_docker_image(self):

        self.mock_UninstallComponents.uninstall_docker_image('image1', '1.2.1', self.mock_UninstallComponents.mock_docker_api)
        self.mock_UninstallComponents.mock_docker_api.delete_image.assert_called_once_with('image1', '1.2.1')
			
    def test_uninstall_docker_image_err(self):
	
        self.mock_UninstallComponents.mock_docker_api.delete_image.side_effect= ProductInstallException(
        "Error occurred")
		
        with self.assertRaises(ProductInstallException):
            self.mock_UninstallComponents.uninstall_docker_image('image1', 'version1', self.mock_UninstallComponents.mock_docker_api)
		
        self.mock_UninstallComponents.mock_docker_api.delete_image.assert_called_once_with('image1', 'version1', self.mock_UninstallComponents.mock_docker_api)
		
        self.mock_print.assert_called_once_with(
            "Failed to remove image image1:version1: Error occured")
		
    def test_uninstall_s3_artifacts(self):
		
        self.mock_UninstallComponents.uninstall_s3_artifacts('bucket1', 'key1')
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_called_once_with('bucket1', 'key1')
		
    def test_uninstall_s3_artifacts_err(self):
	
        self.mock_UninstallComponents.mock_subprocess.check_output.side_effect= ProductInstallException(
        "Error occurred")
	    	
        with self.assertRaises(ProductInstallException):
            self.mock_UninstallComponents.uninstall_s3_artifacts('bucket1', 'key1')
	
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_called_once_with('bucket1', 'key1')
        self.mock_print.assert_called_once_with("Failed to remove bucket1:key1 from S3 artifacts")
		
    def test_uninstall_hosted_repos(self):

        self.mock_UninstallComponents.uninstall_hosted_repos('repo1', self.mock_UninstallComponents.mock_nexus_api)
        self.mock_UninstallComponents.mock_nexus_api.repos.delete.assert_called_once_with('repo1')
	
    def test_uninstall_hosted_repos_err(self):
	
        self.mock_UninstallComponents.mock_nexus_api.repos.delete.side_effect = ProductInstallException(
        "Error occurred" )
	
        with self.assertRaises(ProductInstallException):
            self.mock_UninstallComponents.uninstall_hosted_repos('repo1', self.mock_UninstallComponents.mock_nexus_api)
	
        self.mock_print.assert_called_once_with("Failed to remove repository repo1")
		
    def test_uninstall_helm_charts(self):
	
        self.mock_UninstallComponents.uninstall_helm_charts('chart1', 'version1', 'nexus_id', self.mock_UninstallComponents.mock_nexus_api)
        self.mock_UninstallComponents.mock_nexus_api.components.delete.assert_called_once_with('nexus_id')
	
    def test_uninstall_helm_charts_err(self):
	
        self.mock_UninstallComponents.mock_nexus_api.components.delete.side_effect=ProductInstallException(
        "Error occurred" )
	   
        with self.assertRaises(ProductInstallException):
            self.mock_UninstallComponents.uninstall_helm_charts('chart1', 'version1', 'nexus_id', self.mock_UninstallComponents.mock_nexus_api)
	
        self.mock_print.assert_called_once_with("Failed to remove helm chart chart1 ")
	
    def test_uninstall_loftsman_manifests(self):
	
        mock_manifest_keys = [ 'manifest1', 'manifest2']
	
        self.mock_UninstallComponents.uninstall_loftsman_manifests(mock_manifest_keys)
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_any_call('manifest1')
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_any_call('manifest2')
	
    def test_uninstall_loftsman_manifests_err(self):
		
        mock_manifest_keys = [ 'manifest1', 'manifest2']
		
        self.mock_UninstallComponents.mock_subprocess.check_output.side_effect = ProductInstallException(
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
		
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_called_once_with('cmd1')
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_called_once_with('cmd_s3')
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_called_once_with('cmd_ims')
	
    def test_uninstall_ims_recipies_err(self):
	
        self.mock_UninstallComponents.mock_subprocess.check_output.side_effect = ProductInstallException(
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

        self.mock_UninstallComponents.mock_subprocess.check_output.assert_called_once_with('cmd1')
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_called_once_with('cmd_s3')
        self.mock_UninstallComponents.mock_subprocess.check_output.assert_called_once_with('cmd_ims')

    def test_uninstall_ims_images_err(self):

        self.mock_UninstallComponents.mock_subprocess.check_output.side_effect = ProductInstallException(
         "Error occurred" )

        with self.assertRaises(ProductInstallException) as context:
            self.mock_UninstallComponents.uninstall_ims_recipies('image1', 'image_id1')

        self.mock_print.assert_called_once_with("Failed to remove IMS image image1")

class TestDeleteProductComponent(unittest.TestCase):

    def setUp(self):
        """Set up mocks"""
        self.mock_delete_product_component= DeleteProductComponent()
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
        self.mock_print.assert_called_once_with(
            "Not removing Docker image image1:version1 used by the following other product versions: mock_similar_product"
        )
    
    def test_remove_product_docker_images_error(self):
        """Test removing docker images with ProductInstallException error"""
        mock_product= Mock()
        mock_product.docker_images=[('image1','version1')]
        self.mock_delete_product_component.get_product.return_value= mock_product

        self.mock_delete_product_component.uninstall_component.uninstall_docker_image.side_effect= ProductInstallException(
            "Error occurred"
        )

        with self.assertRaises(ProductInstallException):
            self.mock_delete_product_component.remove_product_docker_images()
        
        self.mock_delete_product_component.uninstall_component.uninstall_docker_image.assert_called_once_with(
            'image1','version1', self.mock_delete_product_component.mock_docker_api
        )
        self.mock_print.assert_called_once_with(
            "Failed to remove image1:version1: Error occurred"
        )

    
    def test_remove_product_S3_artifacts(self):
        """Test removing product S3 artifacts"""
        mock_product=Mock()
        mock_product.s3_artifacts=[('bucket1','key1'),('bucket2','key2')]
        self.mock_delete_product_component.get_product.return_value=mock_product

        
        self.mock_delete_product_component.remove_product_S3_artifacts()

        self.mock_delete_product_component.uninstall_component.uninstall_S3_artifact.assert_any_call(
            'bucket1','key1'
        )

        self.mock_delete_product_component.uninstall_component.uninstall_S3_artifact.assert_any_call(
            'bucket2', 'key2'
        )

        self.mock_print.assert_called_with("Will be removing the following artifact - bucket2:key2")
        self.mock_print.assert_called_with("Will be removing the following artifact - bucket1:key1")


    def test_remove_product_S3_artifacts_shared_artifacts(self):
        """Test removing S3 artifacts shared by any other product"""
        mock_product=Mock()
        mock_product.s3_artifacts=[('bucket1','key1')]
        self.mock_delete_product_component.get_product.return_value=mock_product

        mock_similar_product=Mock()
        mock_similar_product.s3_artifacts=[('bucket1','key1')]

        self.mock_delete_product_component.products=[mock_similar_product]

        
        self.mock_delete_product_component.remove_product_S3_artifacts()

        self.mock_delete_product_component.uninstall_component.uninstall_S3_artifact.assert_not_called()

        self.mock_print.assert_called_once_with(
                "Not removing S3 artifact bucket1:key1 used by the following other product versions: mock_similar_product"
            )

    def test_remove_product_S3_artifacts_error(self):
        """Test removing S3 artifacts with ProductInstallException error"""
        mock_product=Mock()
        mock_product.s3_artifacts=[('bucket1','key1')]
        self.mock_delete_product_component.get_product.return_value=mock_product

        self.mock_delete_product_component.uninstall_component.uninstall_S3_artifact.side_effect= ProductInstallException(
            "Error occurred"
        )

        with self.assertRaises(ProductInstallException):
            self.mock_delete_product_component.remove_product_S3_artifacts()

        self.mock_delete_product_component.uninstall_component.uninstall_S3_artifact.assert_called_once_with(
            'bucket1','key1'
        )

        
        self.mock_print.assert_called_once_with("Failed to remove bucket1:key1: Error occurred")

    def test_remove_product_helm_charts(self):
        """Test removing product helm charts"""
        mock_product=Mock()
        mock_product.helm=[('chart1','version1')]
        self.mock_delete_product_component.get_product.return_value= mock_product

        nexus_chart=Mock()
        nexus_chart.name= 'chart1'
        nexus_chart.version='version1'
        nexus_chart.id='chart1_id'
        self.mock_delete_product_component.mock_nexus_api.components.list.return_value.components= [nexus_chart]


        self.mock_delete_product_component.remove_product_helm_charts()

        self.mock_delete_product_component.uninstall_component.uninstall_helm_charts.assert_called_once_with(
            'chart1','version1',self.mock_delete_product_component.mock_nexus_api, 'chart1_id'
        )

        self.mock_print.assert_called_once_with("Will be removing the following chart - chart1:version1")


    def test_remove_product_helm_charts_no_charts(self):
        mock_product=Mock()
        mock_product.helm=[]
        self.mock_delete_product_component.get_product.return_value= mock_product

        self.mock_delete_product_component.remove_product_helm_charts()

        self.mock_delete_product_component.uninstall_component.uninstall_helm_charts.assert_not_called()
        self.mock_print.assert_called_once_with("No helm charts found in the configmap data for ")

    def test_remove_product_helm_charts_shared_chart(self):
        """Test removing helm charts shared by any other product"""
        mock_product=Mock()
        mock_product.helm=[('chart1','version1')]
        self.mock_delete_product_component.get_product.return_value= mock_product

        mock_similar_product=Mock()
        mock_similar_product.helm=[('chart1','version1')]
        self.mock_delete_product_component.products= [mock_similar_product]

        self.mock_delete_product_component.remove_product_helm_charts()

        self.mock_delete_product_component.uninstall_component.uninstall_helm_charts.assert_not_called()

        self.mock_print.assert_called_once_with("Not removing Helm chart chart1:version1 used by the following other product versions: mock_similar_product")
    

    def test_remove_product_helm_charts_error_loading_nexus_component(self):
        mock_product=Mock()
        mock_product.helm=[('chart1','version1')]
        self.mock_delete_product_component.get_product.return_value= mock_product

        self.mock_delete_product_component.mock_nexus_api.components.list.side_effect= HTTPError(
            url='http://nexus', code=500, msg= 'Interanl Server Error', hdrs=None, fp=None
        )

        with self.assertRaises(ProductInstallException) as context:
            self.mock_delete_product_component.remove_product_helm_charts()

        self.assertEqual(str(context.exception), "Failed to load Nexus components for 'charts' repository: HTTPError: Internal Server Error")


    def test_remove_product_helm_charts_error(self):
        """Test removing helm charts with ProductInstallException error"""
        mock_product=Mock()
        mock_product.helm=[('chart1','version1')]
        self.mock_delete_product_component.get_product.return_value= mock_product

        nexus_chart=Mock()
        nexus_chart.name= 'chart1'
        nexus_chart.version='version1'
        nexus_chart.id='chart1_id'
        self.mock_delete_product_component.mock_nexus_api.components.list.return_value.components= [nexus_chart]


        self.mock_delete_product_component.uninstall_component.uninstall_helm_charts.side_effect= ProductInstallException(
            "Error occurred"
        )

        with self.assertRaises(ProductInstallException):
            self.mock_delete_product_component.remove_product_helm_charts()     

        self.mock_delete_product_component.uninstall_component.uninstall_helm_charts.assert_once_called_with(
            'chart1','version1', self.mock_delete_product_component.mock_nexus_api, 'chart1_id'
        )

        self.mock_print.assert_called_once_with("Failed to remove chart1:version1: Error occurred")

    def test_remove_product_loftsman_manifests(self):
        mock_product = Mock()
        mock_product.loftsman_manifests = ['manifest1', 'manifest2']
        self.mock_delete_product_component.get_product.return_value = mock_product
        
        self.mock_delete_product_component.remove_product_loftsman_manifests()

        self.mock_delete_product_component.uninstall_component.uninstall_loftsman_manifests.assert_called_once_with(
            ['manifest1', 'manifest2']
        )

        self.mock_print.assert_called_once_with("Manifests to remove are - ['manifest1', 'manifest2']")

    def test_remove_product_loftsman_manifests_error(self):
        mock_product = Mock()
        mock_product.loftsman_manifests = ['manifest1', 'manifest2']
        self.mock_delete_product_component.get_product.return_value = mock_product

        self.mock_delete_product_component.uninstall_component.uninstall_loftsman_manifests.side_effect = ProductInstallException(
            "Error occurred"
        )

        with self.assertRaises(ProductInstallException) as context:
            self.mock_delete_product_component.remove_product_loftsman_manifests()

        self.assertEqual(
            str(context.exception),
            "One or more errors occurred while removing loftsman manifests for name version \n Error occurred"
        )


    def test_remove_ims_recipes(self):
        mock_product = Mock()
        mock_product.recipes = ['recipe1', 'recipe2']
        self.mock_delete_product_component.get_product.return_value = mock_product

        self.mock_delete_product_component.remove_ims_recipes()

        self.mock_delete_product_component.uninstall_component.uninstall_ims_recipes.assert_called_once_with(
            ['recipe1', 'recipe2']
        )

        self.mock_print.assert_called_once_with("ims recipes to remove are - ['recipe1', 'recipe2']")

    def test_remove_ims_recipes_error(self):
        mock_product = Mock()
        mock_product.recipes = ['recipe1', 'recipe2']
        self.mock_delete_product_component.get_product.return_value = mock_product

        self.mock_delete_product_component.uninstall_component.uninstall_ims_recipes.side_effect = ProductInstallException(
            "Error occurred"
        )

        with self.assertRaises(ProductInstallException) as context:
            self.mock_delete_product_component.remove_ims_recipes()

        self.assertEqual(
            str(context.exception),
            "One or more errors occurred while removing IMS recipes for name version \n Error occurred"
        )

    def test_remove_ims_images(self):
        mock_product = Mock()
        mock_product.images = ['image1', 'image2']
        self.mock_delete_product_component.get_product.return_value = mock_product

        self.mock_delete_product_component.remove_ims_images()

        self.mock_delete_product_component.uninstall_component.uninstall_ims_images.assert_called_once_with(
            ['image1', 'image2']
        )
        self.mock_print.assert_called_once_with("IMS images to remove are - ['image1', 'image2']")

    def test_remove_ims_images_error(self):
        mock_product = Mock()
        mock_product.images = ['image1', 'image2']
        self.mock_delete_product_component.get_product.return_value = mock_product

        self.mock_delete_product_component.uninstall_component.uninstall_ims_images.side_effect = ProductInstallException(
            "Error occurred"
        )

        with self.assertRaises(ProductInstallException) as context:
            self.mock_delete_product_component.remove_ims_images()

        self.assertEqual(
            str(context.exception),
            "One or more errors occurred while removing IMS images for name version \n Error occurred"
        )
    
    def test_remove_product_hosted_repos(self):
        mock_product = Mock()
        mock_product.hosted_repositories = ['repo1', 'repo2']
        self.mock_delete_product_component.get_product.return_value = mock_product

        self.mock_delete_product_component.remove_product_hosted_repos()

        self.mock_delete_product_component.uninstall_component.uninstall_hosted_repos.assert_called_once_with(
            ['repo1', 'repo2'], self.mock_delete_product_component.mock_nexus_api
        )

        self.mock_print.assert_called_once_with("Hosted repositories to remove are - ['repo1', 'repo2']")

    def test_remove_product_hosted_repos_error(self):
        mock_product = Mock()
        mock_product.hosted_repositories = ['repo1', 'repo2']
        self.mock_delete_product_component.get_product.return_value = mock_product

        self.mock_delete_product_component.uninstall_component.uninstall_hosted_repos.side_effect = ProductInstallException(
            "Error occurred"
        )

        with self.assertRaises(ProductInstallException) as context:
            self.mock_delete_product_component.remove_product_hosted_repos()

        self.assertEqual(
            str(context.exception),
            "One or more errors occurred while removing hosted repos for name version \n Error occurred"
        )

    def test_remove_product_entry(self):
        self.mock_delete_product_component.pname = 'product1'
        self.mock_delete_product_component.pversion = 'version1'
        self.mock_delete_product_component.name = 'configmap1'
        self.mock_delete_product_component.namespace = 'namespace1'

        with patch.dict('os.environ', {
            'PRODUCT': 'product1',
            'PRODUCT_VERSION': 'version1',
            'CONFIG_MAP': 'configmap1',
            'CONFIG_MAP_NS': 'namespace1',
            'VALIDATE_SCHEMA': 'true'
        }), patch.object(subprocess, 'check_output') as mock_check_output:
            self.mock_delete_product_component.remove_product_entry()

            mock_check_output.assert_called_once_with(['catalog_delete'])
            self.mock_print.assert_called_once_with("Deleted configmap1-version1 from product catalog")

    def test_remove_product_entry_error(self):
        self.mock_delete_product_component.pname = 'product1'
        self.mock_delete_product_component.pversion = 'version1'
        self.mock_delete_product_component.name = 'configmap1'
        self.mock_delete_product_component.namespace = 'namespace1'

        self.mock_delete_product_component.subprocess.check_output.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd='catalog_delete', output='Error occurred'
        )

        with self.assertRaises(ProductInstallException) as context:
            self.mock_delete_product_component.remove_product_entry()

        self.assertEqual(
            str(context.exception),
            "Error removing configmap1-version1 from product catalog: Command 'catalog_delete' returned non-zero exit status 1. Output: Error occurred"
        )

	    
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

