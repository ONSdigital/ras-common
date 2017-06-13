VERSION=`python3 -c "import ons_ras_common; print(ons_ras_common.__version__)"`

all:
	@echo "Current version is: $(VERSION)"

clean:
	@rm -rfv unit-db
	@rm -rfv examples/perfDB

test:
	@rm -f dist/*
	@python3 setup.py sdist
	@python3 setup.py bdist_wheel
	@twine register -r pypitest dist/ons_ras_common-$(VERSION)-py3-none-any.whl
	@twine upload -r pypitest dist/ons_ras_common-$(VERSION).tar.gz

release:
	@twine register -r pypi dist/ons_ras_common-$(VERSION)-py3-none-any.whl
	@twine upload -r pypi dist/ons_ras_common-$(VERSION).tar.gz
