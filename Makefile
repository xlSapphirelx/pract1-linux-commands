PYTHON ?= python3
VFS ?= examples/vfs/deep

.PHONY: run test demo2 demo3 demo4 demo5

run:
	$(PYTHON) src/main.py $(ARGS)

test:
	$(PYTHON) -m unittest discover -s tests -v

demo2:
	bash scripts/stage2_params.sh

demo3:
	bash scripts/stage3_vfs.sh

demo4:
	$(PYTHON) src/main.py --vfs $(VFS) --script examples/startup/stage4.txt

demo5:
	$(PYTHON) src/main.py --vfs $(VFS) --script examples/startup/stage5.txt
