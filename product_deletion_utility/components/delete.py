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
from base64 import b64decode
import warnings

from cray_product_catalog.query import ProductCatalog, ProductCatalogError
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
from kubernetes.client import CoreV1Api
from kubernetes.client.rest import ApiException
from kubernetes.config import load_kube_config, ConfigException
from urllib3.exceptions import MaxRetryError
from urllib.error import HTTPError
from nexusctl import DockerApi, DockerClient, NexusApi, NexusClient
from nexusctl.common import NexusCtlHttpError
from yaml import YAMLLoadWarning

class ProductInstallException(Exception):
    """An error occurred reading or manipulating product installs."""
    pass

class UninstallComponents():
    """"Uninstall individual components of the product version.
    """

    def uninstall_docker_image(self, docker_image_name, docker_image_version, docker_api):
        """Remove a Docker image.
        It is not recommended to call this function directly, instead use
        ProductCatalog.remove_product_docker_images to check that the image
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
            docker_api.delete_image(
                docker_image_name, docker_image_version
            )
            print(f'Successfully removed the docker image {docker_image_short_name}')

        except (HTTPError, NexusCtlHttpError) as err:
            if err.code == 404:
                print(f'{docker_image_short_name} has already been removed')
            else:
                raise ProductInstallException(
                    f'Failed to remove image {docker_image_short_name}: {err}'
                )
        except Exception as e:
            raise ProductInstallException(
                f'Failed to remove image {docker_image_short_name}: {e}'
            )

    def uninstall_S3_artifact(self, s3_bucket, s3_key):
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
                ["cray", "artifacts", "delete", "%s" % s3_bucket, "%s" % s3_key], stderr=subprocess.STDOUT, universal_newlines=True)
            print(f'Successfully removed the artifact {s3_artifact_short_name}')
        except subprocess.CalledProcessError as err:
            if 'not found' in err.output:
                print(f'Artifact {s3_key} not available in S3 bucket - {s3_bucket}')
                print(f'Output of cray artifacts delete is', err.output)
            else:
                raise ProductInstallException(
                    f'Failed to remove S3 artifacts {s3_artifact_short_name} with error: {err}'
                )

    def uninstall_hosted_repos(self, hosted_repo_name, nexus_api):
        """Remove a version's package repositories from Nexus.
        It is not recommended to call this function directly, instead use
        DeleteProductComponent.remove_product_hosted_repos to check that the helm chart
        is not in use by another product.
        Args:
            nexus_api (NexusApi): The nexusctl Nexus API to interface with Nexus.
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing a repository.
        """
        try:
            nexus_api.repos.delete(hosted_repo_name)
            print(f'Successfully removed the repository {hosted_repo_name}')
        except (HTTPError, NexusCtlHttpError) as err:
            if err.code == 404:
                print(f'{hosted_repo_name} has already been removed')
            else:
                raise ProductInstallException(
                    f'Failed to remove repository {hosted_repo_name}: {err}'
                )
        except Exception as e:
            raise ProductInstallException(
                f'Failed to remove repository {hosted_repo_name}: {e}'
            )


    def uninstall_helm_charts(self, chart_name, chart_version, nexus_api, component_nexus_id):
        """Removes a helm chart.
        It is not recommended to call this function directly, instead use
        DeleteProductComponent.remove_product_helm_charts to check that the helm chart
        is not in use by another product.
        Args:
            chart_name   (str): The name of the helm chart to be deleted.
            chart_version(str): The verison of the helm chart to be removed.
            component_nexus_id(str): Nexus ID of the helm chart to be removed.
            nexus_api (NexusApi): The nexusctl Nexus API to interface with Nexus.
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing the helm chart.
        """
        helm_chart_short_name: str = f"{chart_name}:{chart_version}"
        try:
            nexus_api.components.delete(component_nexus_id)
            print(f'Successfully removed the helm chart {helm_chart_short_name}')
        except (HTTPError, NexusCtlHttpError) as err:
            if err.code == 404:
                print(
                    f"Helm chart {helm_chart_short_name} has already been removed")
            else:
                raise ProductInstallException(
                    f"Failed to remove helm chart {helm_chart_short_name} from nexus : {err}")
        except Exception as e:
            raise ProductInstallException(
                f"Failed to remove helm chart {helm_chart_short_name} from nexus : {e}"
            )


    def uninstall_loftsman_manifests(self, manifest_keys):
        """Removes loftsman manifests for a product version from the repo.
        Args:
            manifests (list): List of yaml files containing loftsman manifest
                              for deletion.
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing the artifact.
        """
        try:
            for manifest_key in manifest_keys:
                manifest_key = manifest_key.replace('config-data/','')
                print(f'Removing the following manifest - {manifest_key}')
                output = subprocess.check_output(
                    ["cray", "artifacts", "delete", "config-data", "%s" % manifest_key], stderr=subprocess.STDOUT, universal_newlines=True)
                print(f'Successfully removed the manifest - {manifest_key}')
        except subprocess.CalledProcessError as err:
            if 'not found' in err.output:
                print(f'Manifest {manifest_key} not available in S3 bucket config-data')
                print(f'Output of cray artifacts delete is', err.output)
            raise ProductInstallException(
                f'Failed to remove loftsman manifest {manifest_key} from S3 with error: {err}'
            )

    def uninstall_ims_recipes(self, recipe_name, recipe_id):
        """Removes ims recipes for a product version from the S3.
        Args:
            recipes (list of dictionaries): List of recipe names and ids
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing the IMS recipe.
        """
        try:
            command = "cray artifacts list ims --format json | jq -r '.artifacts[] | select(.Key|test(\"^.*{}.*$\")) | .Key'".format(recipe_id)
            recipe_s3_key = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            print(f'Recipe S3 key is: {recipe_s3_key}')
            if not recipe_s3_key:
                print(f'S3 key could not be retrieved for recipe ID - {recipe_id}')
            else:
                s3_delete_command = "cray artifacts delete ims {}".format(recipe_s3_key)
                output = subprocess.check_output(s3_delete_command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                print(f'Successfully deleted recipe - {recipe_name} from S3')

                ims_delete_command = "cray ims recipes delete {}".format(recipe_id)
                output = subprocess.check_output(ims_delete_command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                print(f'Successfully deleted recipe - {recipe_name} from IMS')

        except subprocess.CalledProcessError as err:
            if 'not found' in err.output:
                print(f'Failed to remove IMS recipe {recipe_name} with error: {err.output}')
            else:
                raise ProductInstallException(
                    f'Failed to remove IMS recipe {recipe_name} with error: {err}'
                )

    def uninstall_ims_images(self, image_name, image_id):
        """Removes ims images for a product version from the S3.
        Args:
            images (list of dictionaries): List of image names and ids
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing the IMS image.
        """
        try:
            command = "cray artifacts list boot-images --format json | jq -r '.artifacts[] | select(.Key|test(\"^.*{}.*$\")) | .Key'".format(image_id)
            image_s3_keys = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            print(f'Image S3 key is {image_s3_keys}')
            if not image_s3_keys:
                print(f'S3 key could not be retrieved for image ID - {image_id}')
            else:
                for image_s3_key in image_s3_keys.rstrip().split('\n'):
                    s3_delete_command = "cray artifacts delete boot-images {}".format(image_s3_key)
                    output = subprocess.check_output(s3_delete_command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                    print(f'Successfully deleted image - {image_name} from S3')

                ims_delete_command = "cray ims images delete {}".format(image_id)
                output = subprocess.check_output(ims_delete_command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                print(f'Successfully deleted image - {image_name} from IMS')

        except subprocess.CalledProcessError as err:
            if 'not found' in err.output:
                print(f'Failed to remove IMS image {image_name} with error: {err.output}')
            else:
                raise ProductInstallException(
                    f'Failed to remove IMS image {image_name} with error: {err}'
                )


class DeleteProductComponent(ProductCatalog):
    """"Inherit the ProductCatalog from cray-product-catalog and add additional methods for supporting deletion of components.
    Delete each component of a product currently installed.
    Attributes:
        name: The product name.
        version: The product version.
    """

    @staticmethod
    def _get_k8s_api():
        """Load a Kubernetes CoreV1Api and return it.
        Returns:
            CoreV1Api: The Kubernetes API.
        Raises:
            ProductInstallException: if there was an error loading the
                Kubernetes configuration.
        """
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=YAMLLoadWarning)
                load_kube_config()
            return CoreV1Api()
        except ConfigException as err:
            raise ProductInstallException(f'Unable to load kubernetes configuration: {err}')

    def _update_environment_with_nexus_credentials(self, secret_name, secret_namespace):
        """Get the credentials for Nexus HTTP API access from a Kubernetes secret.
        Nexusctl expects these to be set as environment variables. If they
        cannot be obtained from a k8s secret, then print a warning and return.
        Args:
            secret_name (str): The name of the secret.
            secret_namespace (str): The namespace of the secret.
        Returns:
            None. Updates os.environ as is expected by Nexusctl.
        """
        try:
            secret = self.k8s_client.read_namespaced_secret(
                secret_name, secret_namespace
            )
        except (MaxRetryError, ApiException):
            print(f'WARNING: unable to read Kubernetes secret {secret_namespace}/{secret_name}')
            return
        if secret.data is None:
            print(f'WARNING: unable to read Kubernetes secret {secret_namespace}/{secret_name}')
            return

        os.environ.update({
            'NEXUS_USERNAME': b64decode(secret.data['username']).decode(),
            'NEXUS_PASSWORD': b64decode(secret.data['password']).decode()
        })

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
        self.catalogname = catalogname
        self.catalognamespace = catalognamespace
        self.uninstall_component = UninstallComponents()
        self.k8s_client = self._get_k8s_api()
        self._update_environment_with_nexus_credentials(
            nexus_credentials_secret_name, nexus_credentials_secret_namespace
        )
        self.docker_api = DockerApi(DockerClient(docker_url))
        self.nexus_api = NexusApi(NexusClient(nexus_url))
        print(f'catalog name and namespace are {self.catalogname}, {self.catalognamespace}')
        # inheriting the properties of parent ProductCatalog class
        super().__init__(self.catalogname, self.catalognamespace)
        try:
            self.product = self.get_product(self.pname, self.pversion)
        except ProductCatalogError as err:
            raise ProductInstallException(f'{err}')

    def remove_product_docker_images(self):
        """Remove a product's Docker images.
        This function will only remove images that are not used by another
        product in the catalog.
        Args:
            None
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing an image.
        """
        images_to_remove = self.product.docker_images
        print(f'Images to remove are - {images_to_remove}')        
        if not images_to_remove:
            print(f"No docker images found in the configmap data for {self.pname}:{self.pversion}")
            return
        other_products = [
            p for p in self.products
            if p.name != self.product.name or p.version != self.product.version
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
                    print(f'Removing the following docker image - {image_name}:{image_version}')
                    self.uninstall_component.uninstall_docker_image(
                        image_name, image_version, self.docker_api)
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {image_name}:{image_version}: {err}')
                    errors = True
                    continue

        if errors:
            raise ProductInstallException(f'One or more errors occurred removing '
                                          f'Docker images for {self.pname} {self.pversion}')

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

        artifacts_to_remove = self.product.s3_artifacts
        print(f'Artifacts to remove are - {artifacts_to_remove}')
        if not artifacts_to_remove:
            print(f"No S3 artifacts found in the configmap data for {self.pname}:{self.pversion}")
            return
        other_products = [
            p for p in self.products
            if p.name != self.product.name or p.version != self.product.version
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
                    print(
                        f'Removing the following artifact - {artifact_bucket}:{artifact_key}')
                    self.uninstall_component.uninstall_S3_artifact(
                        artifact_bucket, artifact_key)
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {artifact_bucket}:{artifact_bucket}: {err}')
                    errors = True
                    continue

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
            ProductInstallException: If an error occurred removing a helm chart.
        """
        charts_to_remove = self.product.helm
        print(f'Charts to remove are - {charts_to_remove}')
        if not charts_to_remove:
            print(f"No helm charts found in the configmap data for {self.pname}:{self.pversion}")
            return
        try:
            nexus_charts = self.nexus_api.components.list("charts")
        except HTTPError as err:
            raise ProductInstallException(
                f"Failed to load Nexus components for 'charts' repository: {err}"
        )
        other_products = [
            p for p in self.products
            if p.name != self.product.name or p.version != self.product.version
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
                    for component in nexus_charts.components:
                        if component.name == chart_name and component.version == chart_version:
                            print(
                                f'Removing the following chart - {chart_name}:{chart_version} with ID {component.id}')
                            self.uninstall_component.uninstall_helm_charts(
                                chart_name, chart_version, self.nexus_api, component.id)
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {chart_name}:{chart_version}: {err}')
                    errors = True
                    continue

        if errors:
            raise ProductInstallException(f'One or more errors occurred while removing '
                                          f'Helm Charts for {self.pname} {self.pversion}')

    def remove_product_loftsman_manifests(self):
        """Remove a product's loftsman manifests.
        Args:
            None
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing loftsman manifest.
        """
        manifests_to_remove = self.product.loftsman_manifests
        print(f'Manifests to remove are - {manifests_to_remove}')
        if not manifests_to_remove:
            print(f"No loftsman manifests found in the configmap data for {self.pname}:{self.pversion}")
            return
        try:
            self.uninstall_component.uninstall_loftsman_manifests(manifests_to_remove)
        except ProductInstallException as err:
            raise ProductInstallException(f'One or more errors occurred while removing '
                                          f'loftsman manifests for {self.pname} {self.pversion} \n {err}')

    def remove_ims_recipes(self):
        """Remove a product's ims recipes.
        Args:
            None
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing an IMS recipe.
        """
        ims_recipes_to_remove = self.product.recipes
        print(f'IMS recipes to remove are - {ims_recipes_to_remove}')
        if not ims_recipes_to_remove:
            print(f"No IMS recipes found in the configmap data for {self.pname}:{self.pversion}")
            return
        other_products = [
            p for p in self.products
            if p.name != self.product.name or p.version != self.product.version
        ]

        errors = False
        # For each recipe to remove, check if it is shared by any other products.
        for recipe in ims_recipes_to_remove:
            recipe_name=recipe['name']
            recipe_id=recipe['id']
            other_products_with_same_recipe = [
                other_product for other_product in other_products
                if any([
                    other_recipe['name'] == recipe_name and other_recipe['id'] == recipe_id
                    for other_recipe in other_product.recipes
                ])
            ]
            if other_products_with_same_recipe:
                print(f'Not removing IMS recipe {recipe_name}:{recipe_id} '
                      f'used by the following other product versions: '
                      f'{", ".join(str(p) for p in other_products_with_same_recipe)}')
            else:
                try:
                    print(
                        f'Removing the following IMS recipe - {recipe_name}:{recipe_id}')
                    self.uninstall_component.uninstall_ims_recipes(
                        recipe_name, recipe_id)
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {recipe_name}:{recipe_id}: {err}')
                    errors = True
                    continue

        if errors:
            raise ProductInstallException(f'One or more errors occurred removing '
                                          f'IMS recipes for {self.pname} {self.pversion}')


    def remove_ims_images(self):
        """Remove a product's ims images.
        Args:
            None
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing an IMS image.
        """
        ims_images_to_remove = self.product.images
        print(f'IMS images to remove are - {ims_images_to_remove}')
        if not ims_images_to_remove:
            print(f"No IMS images found in the configmap data for {self.pname}:{self.pversion}")
            return
        other_products = [
            p for p in self.products
            if p.name != self.product.name or p.version != self.product.version
        ]

        errors = False
        # For each image to remove, check if it is shared by any other products.
        for image in ims_images_to_remove:
            image_name = image['name']
            image_id = image['id']
            other_products_with_same_image = [
                other_product for other_product in other_products
                if any([
                    other_image['name'] == image_name and other_image['id'] == image_id
                    for other_image in other_product.images
                ])
            ]
            if other_products_with_same_image:
                print(f'Not removing IMS image {image_name}:{image_id} '
                      f'used by the following other product versions: '
                      f'{", ".join(str(p) for p in other_products_with_same_image)}')
            else:
                try:
                    print(
                        f'Removing the following IMS image - {image_name}:{image_id}')
                    self.uninstall_component.uninstall_ims_images(
                        image_name, image_id)
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {image_name}:{image_id}: {err}')
                    errors = True
                    continue

        if errors:
            raise ProductInstallException(f'One or more errors occurred removing '
                                          f'IMS images for {self.pname} {self.pversion}')


    def remove_product_hosted_repos(self):
        """Remove a product's hosted repositories.
        Args:
            None
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred uninstalling repositories.
        """
        hosted_repos_to_remove = self.product.hosted_repositories
        print(f'Hosted repositories to remove are - {hosted_repos_to_remove}')
        if not hosted_repos_to_remove:
            print(f"No hosted repos found in the configmap data for {self.pname}:{self.pversion}")
            return
        other_products = [
            p for p in self.products
            if p.name != self.product.name or p.version != self.product.version
        ]

        errors = False
        # For each hosted repo to remove, check if it is shared by any other products.
        for hosted_repo in hosted_repos_to_remove:
            hosted_repo_name = hosted_repo['name']
            hosted_repo_type = hosted_repo['type']
            other_products_with_same_hosted_repo = [
                other_product for other_product in other_products
                if any([
                    other_hosted_repo['name'] == hosted_repo_name and other_hosted_repo['type'] == hosted_repo_type
                    for other_hosted_repo in other_product.hosted_repositories
                ])
            ]
            if other_products_with_same_hosted_repo:
                print(f'Not removing hosted repo {hosted_repo_name} '
                      f'used by the following other product versions: '
                      f'{", ".join(str(p) for p in other_products_with_same_hosted_repo)}')
            else:
                try:
                    print(f'Removing the following hosted repo - {hosted_repo_name}')
                    self.uninstall_component.uninstall_hosted_repos(
                        hosted_repo_name, self.nexus_api)
                except ProductInstallException as err:
                    print(
                        f'Failed to remove {hosted_repo_name} : {err}')
                    errors = True
                    continue
        if errors:
            raise ProductInstallException(f'One or more errors occurred removing '
                                          f'hosted repos for {self.pname} {self.pversion}')

    def remove_product_entry(self):
        """Remove this product version's entry from the product catalog.
        This function uses the catalog_delete script provided by
        cray-product-catalog.
        Args:
            None
        Returns:
            None
        Raises:
            ProductInstallException: If an error occurred removing the entry.
        """
        # Use os.environ so that PATH and VIRTUAL_ENV are used
        os.environ.update({
            'PRODUCT': self.pname,
            'PRODUCT_VERSION': self.pversion,
            'CONFIG_MAP': self.catalogname,
            'CONFIG_MAP_NS': self.catalognamespace,
            'VALIDATE_SCHEMA': 'true'
        })
        try:
            subprocess.check_output(['catalog_delete'])
            print(f'Deleted {self.pname}-{self.pversion} from product catalog')
        except subprocess.CalledProcessError as err:
            raise ProductInstallException(
                f'Error removing {self.pname}-{self.pversion} from product catalog: {err}'
            )
