.PHONY: test

MODULE = zmq_api.py

all:
	@echo "make style"
	@echo "make flakes"
	@echo "make lint"
	@echo "make test_api"
	@echo "make test_test"

style:
	pycodestyle $(MODULE)

flakes:
	pyflakes $(MODULE)

lint:
	pylint $(MODULE)

test_api:
	python3 test/lib_api.py

test_test:
	python3 test/test.py
