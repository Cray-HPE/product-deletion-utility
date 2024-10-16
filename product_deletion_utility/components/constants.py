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
Contains constant values for product-deletion-utility
"""
from nexusctl.common import DEFAULT_DOCKER_REGISTRY_API_BASE_URL
from nexusctl.common import DEFAULT_NEXUS_API_BASE_URL

DEFAULT_DOCKER_URL = DEFAULT_DOCKER_REGISTRY_API_BASE_URL
DEFAULT_NEXUS_URL = DEFAULT_NEXUS_API_BASE_URL
NEXUS_CREDENTIALS_SECRET_NAME = 'nexus-admin-credential'
NEXUS_CREDENTIALS_SECRET_NAMESPACE = 'nexus'
PRODUCT_CATALOG_CONFIG_MAP_NAME = 'cray-product-catalog'
PRODUCT_CATALOG_CONFIG_MAP_NAMESPACE = 'services'
DEFAULT_LOG_DIR = '/etc/cray/upgrade/csm/iuf/deletion'