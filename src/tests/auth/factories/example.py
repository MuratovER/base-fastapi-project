import factory
from factory.base import BaseFactory
from factory.fuzzy import FuzzyChoice

from tests.auth.factories.fakers import UniqueStringFaker


class ExampleFactory(BaseFactory):
    class Meta:
        model = ExampleModel

    first_name = UniqueStringFaker("first_name")
    enum = FuzzyChoice(list(ExampleEnum))
    auth_token = factory.LazyAttribute(lambda _: some_func())

