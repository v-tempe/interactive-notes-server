import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.contrib.auth.models import User
from ..models import Notebook, Section, ContentBlock, Collaborator

fake = Faker()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda x: fake.user_name())
    email = factory.LazyAttribute(lambda x: fake.email())
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')


class NotebookFactory(DjangoModelFactory):
    class Meta:
        model = Notebook

    title = factory.LazyAttribute(lambda x: fake.sentence(nb_words=4))
    owner = factory.SubFactory(UserFactory)


class SectionFactory(DjangoModelFactory):
    class Meta:
        model = Section

    notebook = factory.SubFactory(NotebookFactory)
    title = factory.LazyAttribute(lambda x: fake.sentence(nb_words=3))
    order = factory.Sequence(lambda n: n)


class ContentBlockFactory(DjangoModelFactory):
    class Meta:
        model = ContentBlock

    section = factory.SubFactory(SectionFactory)
    block_type = factory.Iterator(['text', 'code', 'image'])
    content = factory.LazyAttribute(lambda x: fake.text(max_nb_chars=200) if x.block_type != 'image' else '')
    image_url = factory.LazyAttribute(lambda x: fake.image_url() if x.block_type == 'image' else None)
    order = factory.Sequence(lambda n: n)
