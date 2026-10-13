################################################################################
#
# bdsh
#
################################################################################

BDSH_VERSION = 0.6.0
BDSH_SITE = /workspace/bdsh
BDSH_SITE_METHOD = local
BDSH_SETUP_TYPE = pep517
BDSH_LICENSE = LicenseRef-Proprietary
BDSH_LICENSE_FILES = LICENSE
BDSH_DEPENDENCIES = host-python-setuptools python-argon2-cffi python-icmplib python-psutil python-requests

define BDSH_CLEAN_STALE_BUILD_OUTPUT
	rm -rf $(@D)/build $(@D)/dist
endef
BDSH_PRE_CONFIGURE_HOOKS += BDSH_CLEAN_STALE_BUILD_OUTPUT

$(eval $(python-package))
