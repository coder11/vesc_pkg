VESC_TOOL ?= vesc_tool

TARGET = balance

# BUILD_DIR defaults to current directory if not set by parent Makefile
BUILD_DIR ?= .

CONF_GEN_HEADERS = conf/confparser.h conf/confxml.h
CONF_GEN_SOURCES = conf/confparser.c conf/confxml.c
CONF_GEN_FILES = $(CONF_GEN_HEADERS) $(CONF_GEN_SOURCES)
LOCAL_SOURCES = $(wildcard *.c)
SOURCES = $(LOCAL_SOURCES) conf/buffer.c $(CONF_GEN_SOURCES)

VESC_C_LIB_PATH=../../c_libs/
include $(VESC_C_LIB_PATH)rules.mk

# Override OBJECTS to point to BUILD_DIR
# Handle local sources and external sources differently
LOCAL_OBJECTS = $(patsubst %.c,$(BUILD_DIR)/%.so,$(LOCAL_SOURCES)) \
                $(patsubst conf/%.c,$(BUILD_DIR)/conf/%.so,$(filter conf/%,$(SOURCES)))
EXTERNAL_OBJECTS = $(patsubst $(VESC_C_LIB_PATH)%.c,$(BUILD_DIR)/deps/%.so,$(filter $(VESC_C_LIB_PATH)%,$(SOURCES)))
OBJECTS = $(LOCAL_OBJECTS) $(EXTERNAL_OBJECTS)

# Filter DEPS to only include local dependency files (exclude c_libs)
# Also include redirected dependency files for external sources
LOCAL_DEPS = $(patsubst %.c,$(BUILD_DIR)/%.d,$(filter-out $(VESC_C_LIB_PATH)%,$(LOCAL_SOURCES))) \
             $(patsubst conf/%.c,$(BUILD_DIR)/conf/%.d,$(filter conf/%,$(SOURCES)))
EXTERNAL_DEPS = $(filter $(VESC_C_LIB_PATH)%,$(SOURCES))
EXTERNAL_DEPS := $(patsubst $(VESC_C_LIB_PATH)%.c,$(BUILD_DIR)/deps/%.d,$(EXTERNAL_DEPS))
DEPS = $(LOCAL_DEPS) $(EXTERNAL_DEPS)

ADD_TO_CLEAN = $(CONF_GEN_FILES) $(DEPS) $(BUILD_DIR)/deps

CFLAGS += -MMD -flto
LDFLAGS += -flto

# Override the default %.so rule from rules.mk to also output to BUILD_DIR
%.so: %.c
	@mkdir -p $$(dirname $(BUILD_DIR)/$@) $$(dirname $(BUILD_DIR)/$*.d)
	$(CC) $(CFLAGS) -MF $(BUILD_DIR)/$*.d -c $< -o $(BUILD_DIR)/$@

# Override %.so rule to output to BUILD_DIR (for local sources)
$(BUILD_DIR)/%.so: %.c
	@mkdir -p $$(dirname $@) $$(dirname $(BUILD_DIR)/$*.d)
	$(CC) $(CFLAGS) -MF $(BUILD_DIR)/$*.d -c $< -o $@

# Handle conf/ subdirectory sources
$(BUILD_DIR)/conf/%.so: conf/%.c
	@mkdir -p $$(dirname $@) $$(dirname $(BUILD_DIR)/conf/$*.d)
	$(CC) $(CFLAGS) -MF $(BUILD_DIR)/conf/$*.d -c $< -o $@

# Redirect dependency files for external sources to BUILD_DIR/deps directory
# This prevents .d files from being created in c_libs
$(BUILD_DIR)/deps/%.so: $(VESC_C_LIB_PATH)%.c
	@mkdir -p $$(dirname $@) $$(dirname $(BUILD_DIR)/deps/$*.d)
	$(CC) $(CFLAGS) -MF $(BUILD_DIR)/deps/$*.d -c $< -o $@

# Override TARGET rule to output to BUILD_DIR
$(TARGET): $(OBJECTS)
	@mkdir -p $(BUILD_DIR)
	$(LD) $(OBJECTS) $(LDFLAGS) -o $(BUILD_DIR)/$@.elf
	$(OBJDUMP) -D $(BUILD_DIR)/$@.elf > $(BUILD_DIR)/$@.list
	$(OBJCOPY) -O binary $(BUILD_DIR)/$@.elf $(BUILD_DIR)/$@.bin --gap-fill 0x00
	$(PYTHON) $(VESC_C_LIB_PATH)/conv.py -f $(BUILD_DIR)/$@.bin -n $@ > $(BUILD_DIR)/$@.lisp

main.c: $(CONF_GEN_HEADERS)

$(CONF_GEN_FILES) &: conf/settings.xml
	$(VESC_TOOL) --xmlConfToCode conf/settings.xml

# Override clean to also clean BUILD_DIR and any stray files in source directory
clean:
	rm -f $(OBJECTS) $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).list $(BUILD_DIR)/$(TARGET).lisp $(BUILD_DIR)/$(TARGET).bin
	rm -rf $(BUILD_DIR)/deps
	rm -f $(ADD_TO_CLEAN)
	# Also clean any build artifacts that might have been created in source directory
	rm -f $(LOCAL_SOURCES:.c=.so) $(LOCAL_SOURCES:.c=.d)
	rm -f conf/*.so conf/*.d

-include $(DEPS)
