################################################################################
#
# python-bdsh
#
################################################################################

PYTHON_BDSH_VERSION = 0.6.0
PYTHON_BDSH_SITE = /workspace/bdsh
PYTHON_BDSH_SITE_METHOD = local
PYTHON_BDSH_SETUP_TYPE = pep517
PYTHON_BDSH_LICENSE = LicenseRef-Proprietary
PYTHON_BDSH_LICENSE_FILES = LICENSE
PYTHON_BDSH_DEPENDENCIES = host-python-setuptools

define PYTHON_BDSH_CLEAN_STALE_BUILD_OUTPUT
	rm -rf $(@D)/build $(@D)/dist
endef
PYTHON_BDSH_PRE_CONFIGURE_HOOKS += PYTHON_BDSH_CLEAN_STALE_BUILD_OUTPUT

$(eval $(python-package))
