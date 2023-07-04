#!/bin/bash
set -e +xv
trap "rm -rf /root/.zypp" EXIT

SLES_REPO_USERNAME=$(cat /run/secrets/ARTIFACTORY_READONLY_USER)
SLES_REPO_PASSWORD=$(cat /run/secrets/ARTIFACTORY_READONLY_TOKEN)
CSM_RPMS_HPE_STABLE="https://${SLES_REPO_USERNAME:-}${SLES_REPO_PASSWORD+:}${SLES_REPO_PASSWORD}@artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/"
SLES_MIRROR="https://${SLES_REPO_USERNAME:-}${SLES_REPO_PASSWORD+:}${SLES_REPO_PASSWORD}@artifactory.algol60.net/artifactory/sles-mirror"
ARCH=x86_64
zypper --non-interactive rr --all
zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Basesystem/15-SP3/${ARCH}/product?auth=basic sles15sp3-Module-Basesystem-product
zypper --non-interactive ar ${SLES_MIRROR}/Updates/SLE-Module-Containers/15-SP4/${ARCH}/update?auth=basic sles15sp4-Module-Containers-update
zypper --non-interactive ar --no-gpgcheck ${CSM_RPMS_HPE_STABLE}/sle-15sp2/?auth=basic CSM-SLE-15SP2
zypper --non-interactive ar --no-gpgcheck ${CSM_RPMS_HPE_STABLE}/sle-15sp3/?auth=basic CSM-SLE-15SP3
zypper update -y
zypper install -y craycli git-core bash
zypper clean -a && zypper --non-interactive rr --all && rm -f /etc/zypp/repos.d/*

