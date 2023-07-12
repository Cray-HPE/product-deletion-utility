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

import subprocess
import os

from cray_product_catalog.query import ProductCatalog, ProductInstallException
from cray_product_catalog.constants import (
    PRODUCT_CATALOG_CONFIG_MAP_NAME,
    PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE,
)
from product_deletion_utility.components.constants import (
    NEXUS_CREDENTIALS_SECRET_NAME,
    NEXUS_CREDENTIALS_SECRET_NAMESPACE,
    DEFAULT_NEXUS_URL,
    DEFAULT_DOCKER_URL,
)
from urllib.error import HTTPError
from nexusctl import DockerApi, DockerClient, NexusApi, NexusClient


class UninstallComponents():
    """"Uninstall individual components of the product version.

    Attributes:
       DockerApi: instance of DockerApi 
       NexusApi: instance of NexusApi
    """

    def __init__(self, docker_url, nexus_url):
        self.docker_api = DockerApi(DockerClient(docker_url))
        self.nexus_api = NexusApi(NexusClient(nexus_url))

    def uninstall_docker_image(docker_image_name, docker_image_version, docker_api):
        """Remove a Docker image.

        It is not recommended to call this function directly, instead use
        ProductCatalog.uninstall_product_docker_images to check that the image
        is not in use by another product.

        Args:
            docker_image_name (str): The name of the Docker image to uninstall.
            docker_image_version (str): The version of the Docker image to uninstall.
            docker_api (DockerApi): The nexusctl Docker API to interface with
                the Docker registry.

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing the image.
        """
        docker_image_short_name = f'{docker_image_name}:{docker_image_version}'
        try:
            repo_list = docker_api.list_repos()
            """docker_api.delete_image(
                docker_image_name, docker_image_version
            )
            print(f'Removed Docker image {docker_image_short_name}')"""
            print(f'Listing all repos')
            print(f'{repo_list}')
        except HTTPError as err:
            if err.code == 404:
                print(f'{docker_image_short_name} has already been removed.')
            else:
                raise ProductInstallException(
                    f'Failed to remove image {docker_image_short_name}: {err}'
                )

    def uninstall_S3_artifact(s3_bucket, s3_key):
        """Removes an S3 artifact.

        It is not recommended to call this function directly, instead use
        DeleteProductComponent.remove_product_S3_artifacts to check that the artifact
        is not in use by another product.

        Args:
            s3_bucket (str): The name of the S3 bucket which has the artifact to be deleted.
            s3_key (str): The key of the artifact to be removed.

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing the artifact.
        """
        s3_artifact_short_name = f'{s3_bucket}:{s3_key}'
        try:
            output = subprocess.check_output(
                ["cray", "artifacts", "list", "boot-images"], text=True)
            print(f'Output of cray artifacts list is {output}')
        except subprocess.CalledProcessError as err:
            raise ProductInstallException(
                f'Failed to remove S3 artifacts {s3_artifact_short_name} with error: {err}'
            )

    def uninstall_hosted_repos(self, nexus_api):
        """Remove a version's package repositories from Nexus.

        Args:
            nexus_api (NexusApi): The nexusctl Nexus API to interface with
            Nexus.

            Returns:
                None

            Raises:
                ProductInstallException: If an error occurred removing a repository.
            """
        errors = False
        for hosted_repo_name in self.hosted_repository_names:
            try:
                nexus_api.repos.delete(hosted_repo_name)
                print(f'Repository {hosted_repo_name} has been removed.')
            except HTTPError as err:
                if err.code == 404:
                    print(f'{hosted_repo_name} has already been removed.')
                else:
                    print(
                        f'Failed to remove hosted repository {hosted_repo_name}: {err}')
                    errors = True
        if errors:
            raise ProductInstallException(
                f'One or more errors occurred uninstalling repositories for {self.name} {self.version}.'
            )

    def uninstall_helm_charts(chart_name, chart_version):
        """Removes a helm chart.

        It is not recommended to call this function directly, instead use
        DeleteProductComponent.remove_product_S3_artifacts to check that the artifact
        is not in use by another product.

        Args:
            chart_name   (str): The name of the helm chart to be deleted.
            chart_version(str): The verison of the helm chart to be removed.

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing the artifact.
        """
        pass

    def uninstall_helm_charts(chart_name, chart_version):
        """Removes a helm chart.

        It is not recommended to call this function directly, instead use
        DeleteProductComponent.remove_product_helm_artifacts to check that the artifact
        is not in use by another product.

        Args:
            chart_name   (str): The name of the helm chart to be deleted.
            chart_version(str): The verison of the helm chart to be removed.

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing the artifact.
        """
        pass

    def uninstall_loftsman_manifests(manifests):
        """Removes loftsman manifests for a product version from the repo.

        Args:
            manifests   (list): List of yaml files containing loftsman manifest 
                                for deletion.

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing the artifact.
        """
        pass

    def uninstall_ims_recipes(recipes):
        """Removes ims images for a product version from the s3.

        Args:
            receipes (list of dictionaries): List of receipes and ids

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing the artifact.
        """
        pass

    def uninstall_ims_images(images):
        """Removes ims images for a product version from the s3.

        Args:
            manifests (list of dictionaries): List of images and ids 
                                for deletion.

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing the artifact.
        """
        pass


class DeleteProductComponent(ProductCatalog):
    """"Inherit the ProductCatalog from cray-product-catalog and add additional methods for supporting deletion of components.

    Delete each component of a product currently installed.

    Attributes:
        name: The product name.
        version: The product version.
    """

    def __init__(self, catalogname=PRODUCT_CATALOG_CONFIG_MAP_NAME,
                 catalognamespace=PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE,
                 productname=None,
                 productversion=None,
                 nexus_url=DEFAULT_NEXUS_URL,
                 docker_url=DEFAULT_DOCKER_URL,
                 nexus_credentials_secret_name=NEXUS_CREDENTIALS_SECRET_NAME,
                 nexus_credentials_secret_namespace=NEXUS_CREDENTIALS_SECRET_NAMESPACE):

        self.pname = productname
        self.pversion = productversion
        self.uninstall_component = UninstallComponents(nexus_url, docker_url)
        # inheriting the properties of parent ProductCatalog class
        super().__init__(catalogname, catalognamespace)

    def remove_product_docker_images(self):
        """Remove a product's Docker images.

        This function will only remove images that are not used by another
        product in the catalog. For images that are used by another

        Args:
            None

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing an image.
        """
        product = self.get_product(self.pname, self.pversion)

        images_to_remove = product.docker_images
        other_products = [
            p for p in self.products
            if p.version != product.version or p.name != product.name
        ]

        errors = False
        # For each image to remove, check if it is shared by any other products.
        for image_name, image_version in images_to_remove:
            other_products_with_same_docker_image = [
                other_product for other_product in other_products
                if any([
                    other_image_name == image_name and other_image_version == image_version
                    for other_image_name, other_image_version in other_product.docker_images
                ])
            ]
            if other_products_with_same_docker_image:
                print(f'Not removing Docker image {image_name}:{image_version} '
                      f'used by the following other product versions: '
                      f'{", ".join(str(p) for p in other_products_with_same_docker_image)}')
            else:
                try:
                    self.uninstall_component.uninstall_docker_image(
                        image_name, image_version, self.docker_api)
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {image_name}:{image_version}: {err}')
                    errors = True

        if errors:
            raise ProductInstallException(f'One or more errors occurred removing '
                                          f'Docker images for {self.pname} {self.pversion}.')

    def remove_product_S3_artifacts(self):
        """Remove a product's S3 artifacts.

        This function will only remove artifacts that are not used by another
        product in the catalog.

        Args:
            None

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing an artifact.
        """
        product = self.get_product(self.pname, self.pversion)

        artifacts_to_remove = product.s3_artifacts
        print(f'Artifacts to remove are - {artifacts_to_remove}')
        other_products = [
            p for p in self.products
            if p.version != product.version or p.name != product.name
        ]

        errors = False
        # For each artifact to remove, check if it is shared by any other products.
        for artifact_bucket, artifact_key in artifacts_to_remove:
            other_products_with_same_artifact_key = [
                other_product for other_product in other_products
                if any([
                    other_artifact_bucket == artifact_bucket and other_artifact_key == artifact_key
                    for other_artifact_bucket, other_artifact_key in other_product.s3_artifacts
                ])
            ]
            if other_products_with_same_artifact_key:
                print(f'Not removing S3 artifact {artifact_bucket}:{artifact_key} '
                      f'used by the following other product versions: '
                      f'{", ".join(str(p) for p in other_products_with_same_artifact_key)}')
            else:
                try:
                    self.uninstall_component.uninstall_S3_artifact(
                        artifact_bucket, artifact_key)
                    print(
                        f'Will be removing the following artifact - {artifact_bucket}:{artifact_key}')
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {artifact_bucket}:{artifact_bucket}: {err}')
                    errors = True

        if errors:
            raise ProductInstallException(f'One or more errors occurred removing '
                                          f'S3 artifacts for {self.pname} {self.pversion}.')

    def remove_product_helm_charts(self):
        """Remove a product's helm charts.

        This function will only remove helm charts that are not used by another
        product in the catalog.

        Args:
            None

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing an artifact.
        """
        product = self.get_product(self.pname, self.pversion)

        charts_to_remove = product.helm
        print(f'Charts to remove are - {charts_to_remove}')
        other_products = [
            p for p in self.products
            if p.version != product.version or p.name != product.name
        ]

        errors = False
        # For each chart to remove, check if it is shared by any other products.
        for chart_name, chart_version in charts_to_remove:
            other_products_with_same_helm_chart = [
                other_product for other_product in other_products
                if any([
                    other_chart_name == chart_name and other_chart_version == chart_version
                    for other_chart_name, other_chart_version in other_product.helm
                ])
            ]
            if other_products_with_same_helm_chart:
                print(f'Not removing Helm chart {chart_name}:{chart_version} '
                      f'used by the following other product versions: '
                      f'{", ".join(str(p) for p in other_products_with_same_helm_chart)}')
            else:
                try:
                    self.uninstall_component.uninstall_helm_charts(
                        chart_name, chart_version)
                    print(
                        f'Will be removing the following chart - {chart_name}:{chart_version}')
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {chart_name}:{chart_version}: {err}')
                    errors = True

        if errors:
            raise ProductInstallException(f'One or more errors occurred removing '
                                          f'Helm Charts for {self.pname} {self.pversion}.')

    def remove_product_loftsman_manifests(self):
        """Remove a product's loftsman manifests.

        Args:
            None

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing an artifact.
        """
        product = self.get_product(self.pname, self.pversion)

        manifests_to_remove = product.loftsman_manifests
        print(f'Manifests to remove are - {manifests_to_remove}')
        self.uninstall_component.uninstall_loftsman_manifests(
            manifests_to_remove)

    def remove_ims_recipes(self):
        """Remove a product's ims receipes.

        Args:
            None

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing an artifact.
        """
        product = self.get_product(self.pname, self.pversion)

        ims_receipes_to_remove = product.recipes
        print(f'ims receipes to remove are - {ims_receipes_to_remove}')
        self.uninstall_component.uninstall_ims_recipes(ims_receipes_to_remove)

    def remove_ims_images(self):
        """Remove a product's ims images.

        Args:
            None

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing an artifact.
        """
        product = self.get_product(self.pname, self.pversion)

        ims_images_to_remove = product.images
        print(f'ims images to remove are - {ims_images_to_remove}')
        self.uninstall_component.uninstall_ims_images(ims_images_to_remove)

    def uninstall_product_hosted_repos(self):
        """Uninstall a product's hosted repositories.

        Args:
            name (str): The name of the product for which to uninstall
                repositories.
            version (str): The version of the product for which to uninstall
                repositories.

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred uninstalling
                repositories.
        """
        product_to_uninstall = self.get_product(self.pname, self.pversion)
        product_to_uninstall.uninstall_hosted_repos(self.nexus_api)

    def remove_product_entry(self):
        """Remove this product version's entry from the product catalog.

        This function uses the catalog_delete script provided by
        cray-product-catalog.

        Args:
            name (str): The name of the product to remove.
            version (str): The version of the product to remove.

        Returns:
            None

        Raises:
            ProductInstallException: If an error occurred removing the entry.
        """
        # Use os.environ so that PATH and VIRTUAL_ENV are used
        os.environ.update({
            'PRODUCT': self.pname,
            'PRODUCT_VERSION': self.pversion,
            'CONFIG_MAP': self.name,
            'CONFIG_MAP_NS': self.namespace,
            'VALIDATE_SCHEMA': 'true'
        })
        try:
            subprocess.check_output(['catalog_delete'])
            print(f'Deleted {self.name}-{self.version} from product catalog.')
        except subprocess.CalledProcessError as err:
            raise ProductInstallException(
                f'Error removing {self.name}-{self.version} from product catalog: {err}'
            )
