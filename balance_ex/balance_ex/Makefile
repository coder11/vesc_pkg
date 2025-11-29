VESC_TOOL ?= vesc_tool

TARGET = balance

CONF_GEN_HEADERS = conf/confparser.h conf/confxml.h
CONF_GEN_SOURCES = conf/confparser.c conf/confxml.c
CONF_GEN_FILES = $(CONF_GEN_HEADERS) $(CONF_GEN_SOURCES)
LOCAL_SOURCES = $(wildcard *.c)
SOURCES = $(LOCAL_SOURCES) conf/buffer.c $(CONF_GEN_SOURCES)

VESC_C_LIB_PATH=../../c_libs/
include $(VESC_C_LIB_PATH)rules.mk

# Filter DEPS to only include local dependency files (exclude c_libs)
# Also include redirected dependency files for external sources
LOCAL_DEPS = $(filter-out $(VESC_C_LIB_PATH)%,$(SOURCES:.c=.d))
EXTERNAL_DEPS = $(filter $(VESC_C_LIB_PATH)%,$(SOURCES))
EXTERNAL_DEPS := $(patsubst $(VESC_C_LIB_PATH)%.c,deps/%.d,$(EXTERNAL_DEPS))
DEPS = $(LOCAL_DEPS) $(EXTERNAL_DEPS)

ADD_TO_CLEAN = $(CONF_GEN_FILES) $(DEPS) deps

CFLAGS += -MMD -flto
LDFLAGS += -flto

# Redirect dependency files for external sources to local deps directory
# This prevents .d files from being created in c_libs
$(VESC_C_LIB_PATH)%.so: $(VESC_C_LIB_PATH)%.c
	@mkdir -p $$(dirname deps/$*.d)
	$(CC) $(filter-out -MMD,$(CFLAGS)) -MMD -MF deps/$*.d -c $< -o $@

main.c: $(CONF_GEN_HEADERS)

$(CONF_GEN_FILES) &: conf/settings.xml
	$(VESC_TOOL) --xmlConfToCode conf/settings.xml

-include $(DEPS)
