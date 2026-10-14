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

define BDSH_CLEAN_STALE_TARGET_PACKAGE
	rm -rf $(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/bdsh \
		$(TARGET_DIR)/usr/lib/python$(PYTHON3_VERSION_MAJOR)/site-packages/bdsh-*.dist-info \
		$(TARGET_DIR)/usr/bin/bdsh \
		$(TARGET_DIR)/usr/bin/bdsh-init \
		$(TARGET_DIR)/usr/bin/boss
endef
BDSH_PRE_INSTALL_TARGET_HOOKS += BDSH_CLEAN_STALE_TARGET_PACKAGE

define BDSH_CLEAN_STALE_BUILD_OUTPUT
	rm -rf $(@D)/build $(@D)/dist
endef
BDSH_PRE_CONFIGURE_HOOKS += BDSH_CLEAN_STALE_BUILD_OUTPUT

$(eval $(python-package))
