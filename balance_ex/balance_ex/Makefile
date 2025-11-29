VESC_TOOL ?= vesc_tool

TARGET = balance

CONF_GEN_HEADERS = conf/confparser.h conf/confxml.h
CONF_GEN_SOURCES = conf/confparser.c conf/confxml.c
CONF_GEN_FILES = $(CONF_GEN_HEADERS) $(CONF_GEN_SOURCES)
SOURCES = main.c conf/buffer.c $(CONF_GEN_SOURCES)
DEPS = $(SOURCES:.c=.d)

ADD_TO_CLEAN = $(CONF_GEN_FILES) $(DEPS)

VESC_C_LIB_PATH=../../c_libs/
include $(VESC_C_LIB_PATH)rules.mk

CFLAGS += -MMD -flto
LDFLAGS += -flto

main.c: $(CONF_GEN_HEADERS)

$(CONF_GEN_FILES) &: conf/settings.xml
	$(VESC_TOOL) --xmlConfToCode conf/settings.xml

-include $(DEPS)
