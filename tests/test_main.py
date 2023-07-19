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


class TestUninstallComponents(unittest.TestCase):
    """Tests for UninstallComponents."""

    def setup(self):
        """Set up mocks"""
        self.mock_docker_api=Mock()
        self.mock_nexus_api=Mock()
        self.mock_print = patch('builtins.print').start()
        
    def tearDown(self):
        """Stop patches."""
        patch.stopall()
    
    def test_uninstall_docker_image(self):
        """Test uninstalling Docker images for an InstalledProductVersion."""
        UninstallComponents.uninstall_docker_image('foo', 'bar', self.mock_docker_api)
        self.mock_docker_api.delete_image.assert_called_once_with('foo', 'bar')

    def test_uninstall_docker_image_not_found(self):
        """Test uninstalling Docker images when image is not found is not an error."""
        self.mock_docker_api.delete_image.side_effect = HTTPError(
            url='http://nexus', code=404, msg='Not found', hdrs=None, fp=None
        )
        UninstallComponents.uninstall_docker_image('foo', 'bar', self.mock_docker_api)
        self.mock_docker_api.delete_image.assert_called_once_with('foo', 'bar')
        self.mock_print.assert_called_once_with('foo:bar has already been removed.')

    def test_uninstall_docker_other_error(self):
        """Test uninstalling Docker images when a non-404 error occurs is an error."""
        http_error = self.mock_docker_api.delete_image.side_effect = HTTPError(
            url='http://nexus', code=503, msg='Nexus problems', hdrs=None, fp=None
        )
        expected_regex = f'Failed to remove image foo:bar: {http_error}'
        with self.assertRaisesRegex(ProductInstallException, expected_regex):
            UninstallComponents.uninstall_docker_image('foo', 'bar', self.mock_docker_api)
        self.mock_docker_api.delete_image.assert_called_once_with('foo', 'bar')


class TestDeleteProductComponent(unittest.TestCase):

    def setup(self):
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
