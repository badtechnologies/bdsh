################################################################################
#
# python-icmplib
#
################################################################################

PYTHON_ICMPLIB_VERSION = 3.0.4
PYTHON_ICMPLIB_SOURCE = icmplib-$(PYTHON_ICMPLIB_VERSION).tar.gz
PYTHON_ICMPLIB_SITE = https://files.pythonhosted.org/packages/6d/78/ca07444be85ec718d4a7617f43fdb5b4eaae40bc15a04a5c888b64f3e35f
PYTHON_ICMPLIB_SETUP_TYPE = setuptools
PYTHON_ICMPLIB_LICENSE = BSD-3-Clause
PYTHON_ICMPLIB_LICENSE_FILES = LICENSE

$(eval $(python-package))
