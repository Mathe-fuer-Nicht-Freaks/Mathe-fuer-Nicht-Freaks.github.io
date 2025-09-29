PLASTEX=plastex
MFNF_RENDERER=python3 mfnf_renderer.py

JOB_NAME=mfnf

BUILD_DIR=build
PLASTEX_OUTPUT=$(BUILD_DIR)/plastex
MFNF_SITE=$(BUILD_DIR)/site

PLASTEX_STATIC_FILES=images,js,styles

.PHONY: all
all:
	$(PLASTEX) --split-level=0 --packages-dirs=packages --extra-templates=templates --theme=mfnftheme --xml --dir=$(PLASTEX_OUTPUT) $(JOB_NAME).tex
	mkdir -p $(MFNF_SITE)
	cp -r $(PLASTEX_OUTPUT)/{$(PLASTEX_STATIC_FILES)} $(MFNF_SITE)
	$(MFNF_RENDERER) $(JOB_NAME) "$(PLASTEX_OUTPUT)" "$(MFNF_SITE)"

.PHONY: clean
clean:
	rm -rf $(BUILD_DIR) $(JOB_NAME).paux
