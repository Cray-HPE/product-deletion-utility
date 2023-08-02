#!/bin/bash
#
# MIT License
#
# (C) Copyright 2022-2023 Hewlett Packard Enterprise Development LP
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
set -e
#
# update-ca-certficates reads from /usr/local/share/ca-certificates
# and updates /etc/ssl/certs/ca-certificates.crt
# REQUESTS_CA_BUNDLE is used by python
#
#export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
#update-ca-certificates 2>/dev/null

# initialize craycli
API_GW="https://api-gw-service-nmn.local"
ADMIN_SECRET=$(kubectl get secrets admin-client-auth -o jsonpath='{.data.client-secret}' | base64 -d)
curl -k -s -d grant_type=client_credentials \
        -d client_id=admin-client \
        -d client_secret=$ADMIN_SECRET https://api-gw-service-nmn.local/keycloak/realms/shasta/protocol/openid-connect/token > /tmp/setup-token.json
export CRAY_CREDENTIALS=/tmp/setup-token.json
cray init --hostname $API_GW --no-auth --overwrite > /dev/null

product-deletion-utility "$@"
