#!/bin/bash
set -e +xv
trap "rm -rf /root/.zypp" EXIT

SLES_REPO_USERNAME=$(cat /run/secrets/ARTIFACTORY_READONLY_USER)
SLES_REPO_PASSWORD=$(cat /run/secrets/ARTIFACTORY_READONLY_TOKEN)
CSM_RPMS_HPE_STABLE="https://${SLES_REPO_USERNAME:-}${SLES_REPO_PASSWORD+:}${SLES_REPO_PASSWORD}@artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/"
SLES_MIRROR="https://${SLES_REPO_USERNAME:-}${SLES_REPO_PASSWORD+:}${SLES_REPO_PASSWORD}@artifactory.algol60.net/artifactory/sles-mirror"
ARCH=x86_64
zypper --non-interactive rr --all
zypper --non-interactive ar ${SLES_MIRROR}/Products/SLE-Module-Basesystem/15-SP4/${ARCH}/product?auth=basic sles15sp4-Module-Basesystem-product
zypper --non-interactive ar --no-gpgcheck ${CSM_RPMS_HPE_STABLE}/sle-15sp4/?auth=basic CSM-SLE-15SP4
zypper update -y
zypper install -y craycli git-core bash python3
zypper clean -a && zypper --non-interactive rr --all && rm -f /etc/zypp/repos.d/*
