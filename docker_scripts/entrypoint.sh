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
set -ex
#
# update-ca-certficates reads from /usr/local/share/ca-certificates
# and updates /etc/ssl/certs/ca-certificates.crt
# REQUESTS_CA_BUNDLE is used by python
#
#update-ca-certificates 2>/dev/null

#export REQUESTS_CA_BUNDLE=/var/lib/ca-certificates/ca-bundle.pem
#export REQUESTS_CA_BUNDLE=/etc/ssl/ca-bundle.pem
#export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
#export REQUESTS_CA_BUNDLE=/opt/venv/lib64/python3.6/site-packages/certifi/cacert.pem

#export REQUESTS_CA_BUNDLE=/etc/pki/trust/anchors/ca-bundle.pem
#cp /etc/ssl/ca-bundle.pem /etc/pki/trust/anchors/
#export REQUESTS_CA_BUNDLE=/usr/local/share/ca-certificates/platform-ca-certs.crt

env
ls /usr/local/share/ca-certificates/
ls /etc/pki/trust/anchors/
ls -al /var/lib/ca-certificates/
#chown nobody:nobody /var/lib/ca-certificates/
#su nobody -g nobody
export REQUESTS_CA_BUNDLE=/var/lib/ca-certificates/ca-bundle.pem
env
export SSL_CERT_DIR=/var/lib/ca-certificates/
#update-ca-certificates -v
product-deletion-utility "$@"
