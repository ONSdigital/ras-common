VERSION=`python3 -c "from ons_ras_common.ons_version import __version__; print(__version__)"`

all:
	@echo "Current version is: $(VERSION)"
	@rm -f dist/*
	@python3 setup.py sdist
	@python3 setup.py bdist_wheel

clean:
	@rm -rfv unit-db
	@rm -rfv examples/perfDB

check:
	@rm -f dist/*
	@python3 setup.py sdist
	@python3 setup.py bdist_wheel
	@twine register -r pypitest dist/ons_ras_common-$(VERSION)-py2.py3-none-any.whl
	@twine upload -r pypitest dist/ons_ras_common-$(VERSION).tar.gz

release:
	@twine register -r pypi dist/ons_ras_common-$(VERSION)-py2.py3-none-any.whl
	@twine upload -r pypi dist/ons_ras_common-$(VERSION).tar.gz
