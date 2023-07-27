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
# Dockerfile for product_deletion_utility

FROM artifactory.algol60.net/csm-docker/stable/docker.io/library/alpine:3.16

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

ENV INSTALLDIR="/deletion"

COPY CHANGELOG.md README.md ${INSTALLDIR}/
COPY setup.py ${INSTALLDIR}/
COPY requirements.lock.txt ${INSTALLDIR}/requirements.txt
COPY tools ${INSTALLDIR}/tools
COPY product_deletion_utility ${INSTALLDIR}/product_deletion_utility
COPY docker_scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# For external dependencies, always pull from internal-pip-stable-local

# TODO: stop pulling from internal artifactory when nexusctl is open source.
ARG PIP_EXTRA_INDEX_URL="https://arti.hpc.amslabs.hpecorp.net/artifactory/internal-pip-stable-local/ \
    https://artifactory.algol60.net/artifactory/csm-python-modules/simple/ \
    https://artifactory.algol60.net/artifactory/csm-python-modules/unstable"

#wget https://artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp4/craycli/x86_64/craycli-0.82.8-1.x86_64.rpm && \
# RUN does not support ENVs, so specify INSTALLDIR explicitly.
RUN --mount=type=secret,id=netrc,target=/root/.netrc --mount=type=secret,id=ARTIFACTORY_READONLY_USER --mount=type=secret,id=ARTIFACTORY_READONLY_TOKEN \
    apk update && apk add --no-cache python3 git bash build-base python3-dev curl rpm && \
    rpm --version && \
    SLES_REPO_USERNAME=$(cat /run/secrets/ARTIFACTORY_READONLY_USER) && \
    SLES_REPO_PASSWORD=$(cat /run/secrets/ARTIFACTORY_READONLY_TOKEN) && \
    echo ${SLES_REPO_USERNAME} && \
    echo ${SLES_REPO_PASSWORD} && \
    wget https://${SLES_REPO_USERNAME:-}${SLES_REPO_PASSWORD+:}${SLES_REPO_PASSWORD}@artifactory.algol60.net/artifactory/csm-rpms/hpe/stable/sle-15sp4/craycli/x86_64/craycli-0.82.8-1.x86_64.rpm && \
    #wget https://arti.hpc.amslabs.hpecorp.net/artifactory/csm-rpms-remote/hpe/stable/sle-15sp4/craycli/x86_64/craycli-0.82.8-1.x86_64.rpm && \
    rpm -i craycli-0.82.8-1.x86_64.rpm && \
    python3 -m venv $VIRTUAL_ENV && \
    pip install --no-cache-dir -U pip && \
    #git clone https://github.com/Cray-HPE/craycli.git && \
    #python3 -m pip install craycli/ && \
    cray --version  && \
    rm -rf craycli/ && \    
    pip install --no-cache-dir /deletion/ && \
    rm -rf /deletion/ && \
    # install kubectl
    curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x ./kubectl && mv ./kubectl /usr/local/bin/kubectl

ENTRYPOINT ["/entrypoint.sh"]
