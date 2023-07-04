# Product Deletion Utility

The product deletion utility is a tool for deleting product components installed through the Installation and Upgrade Framework (IUF).
This utility is launched by `prodmgr` tool for performing delete operations.
This utility internally uses `shasta-install-utility-common` for performing actual deletion.

## Usage

To launch the utility independently, pull the image on the system and follow the format from the example below -

```commandline
podman run --rm --mount type=bind,src=/etc/kubernetes/admin.conf,target=/root/.kube/config,ro=true --mount type=bind,src=/etc/pki/trust/anchors,target=/usr/local/share/ca-certificates,ro=true artifactory.algol60.net/csm-docker/stable/product-deletion-utility:0.0.1 delete cos 2.5.101
```

## Built With

* Opensuse
* Python 3
* Python Requests
* Docker
* [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
* [Gitversion](https://gitversion.net)
* Good intentions

### Dependencies

Note that this container image requires the following dependencies:

- craycli
- git
- bash
- Various python packages as listed in [REQUIREMENTS](requirements.lock.txt)

## Contributing

When CONTRIBUTING, update the [CHANGELOG](CHANGELOG.md) with the new version and the change made.

## Changelog

See the [CHANGELOG](CHANGELOG.md) for changes. This file uses the [Keep A Changelog](https://keepachangelog.com)
format.

## Copyright and License
This project is copyrighted by Hewlett Packard Enterprise Development LP and is under the MIT
license. See the [LICENSE](LICENSE) file for details.
