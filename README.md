# Product Deletion Utility

The product deletion utility is a tool for deleting product components installed through the Installation and Upgrade Framework (IUF).
This utility is launched by `prodmgr` tool for performing delete operations.
This utility internally uses `DockerApi, NexusApi, craycli` for performing actual deletion of different components of a product version.

## Arguments
```text
The following arguments can be passed to `podman` when launching this container independently:

  --product-catalog-name PRODUCT_CATALOG_NAME
                        The name of the product catalog Kubernetes ConfigMap
  --product-catalog-namespace PRODUCT_CATALOG_NAMESPACE
                        The namespace of the product catalog Kubernetes
                        ConfigMap
  --kube-config-src-file KUBE_CONFIG_SRC_FILE
                        The location of the kubernetes configuration file on
                        the host
  --kube-config-target-file KUBE_CONFIG_TARGET_FILE
                        The location where the kubernetes configuration file
                        should be mounted in the container
  --cert-src-dir CERT_SRC_DIR
                        The directory on the host containing trusted
                        certificates
  --cert-target-dir CERT_TARGET_DIR
                        The directory where trusted certificates should be
                        mounted in the container
  --container-registry-hostname CONTAINER_REGISTRY_HOSTNAME
                        The hostname of the container image registry
  --deletion-image-name DELETION_IMAGE_NAME
                        The full path and file name of the deletion image
  --deletion-image-version DELETION_IMAGE_VERSION
                        The version of the deletion image
  -d, --dry-run         Lists the components that would be deleted for the
                        provided product:version

```

The default values for these arguments are:

```text

+-----------------------------------------------------------------------------+
Argument                     Default Value
+-----------------------------------------------------------------------------+
product-catalog-name         'cray-product-catalog'
product-catalog-namespace    'services'
kube-config-src-file         '/etc/kubernetes/admin.conf'
kube-config-target-file      '$HOME/.kube/config'
cert-src-dir                 '/var/lib/ca-certificates'
cert-target-dir              '/var/lib/ca-certificates'
container-registry-hostname  'registry.local'
deletion-image-name          'artifactory.algol60.net/csm-docker/stable/ product-deletion-utility'
deletion-image-version       '1.0.0-product-deletion-utility'
dry-run                      false


```

## Usage

To launch the utility independently, pull the image on the system and follow the format from the example below -

```commandline
podman run --rm --mount type=bind,src=/etc/kubernetes/admin.conf,target=/root/.kube/config, ro=true --mount type=bind,src=/var/lib/ca-certificates,target=/var/lib/ca-certificates,ro=true --mount type=bind,src=/etc/cray/upgrade/csm/iuf/deletion,target=/etc/cray/upgrade/csm/iuf/deletion,ro=false artifactory.algol60.net/csm-docker/stable/product-deletion-utility:0.0.1 delete cos 2.5.101
```
A dry-run option is also supported to simulate the deletion.

Note: Ensure that /etc/cray/upgrade/csm/iuf/deletion directory is created before launching.

## Built With

* Opensuse
* Python 3
* Python Requests
* Docker
* [Git](https://git-scm.com/)
* Good intentions

### Dependencies

Note that this container image requires the following dependencies:

- craycli
- git
- bash
- curl
- jq
- Various python packages as listed in [REQUIREMENTS](requirements.lock.txt)

## Contributing

When CONTRIBUTING, update the [CHANGELOG](CHANGELOG.md) with the new version and the change made.

## Changelog

See the [CHANGELOG](CHANGELOG.md) for changes. This file uses the [Keep A Changelog](https://keepachangelog.com)
format.

## Copyright and License
This project is copyrighted by Hewlett Packard Enterprise Development LP and is under the MIT license. See the [LICENSE](LICENSE) file for details.
