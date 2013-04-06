#!/usr/bin/python
# encoding: utf-8
from django.test import TestCase
from .. import BaseImporter
from cStringIO import StringIO
from django.db import models
import os
from django.core.files  import File as DjangoFile


class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.CharField(max_length=10)

    def save(self, *args, **kwargs):
        return self.full_clean() == None


person_content = """first_name,last_name,age\ntest_first_name_1,test_last_name_1,age1\ntest_first_name_2,test_last_name_2,age2\ntest_first_name_3,test_last_name_3,age3"""


class TestBaseWithModel(TestCase):
    def setUp(self):
        class TestMeta(BaseImporter):
            class Meta:
                model = Person
                delimiter = ','
                raise_errors = True
                ignore_first_line = True

        self.importer = TestMeta(source=person_content.split('\n'))

    def test_get_fields_from_model(self):
        self.assertEquals(self.importer.fields, ['first_name', 'last_name', 'age'])

    def test_values_is_valid(self):
        self.assertTrue(self.importer.is_valid())

    def test_cleaned_data_content(self):
        content = {'first_name': 'test_first_name_1',
            'last_name': 'test_last_name_1', 'age': 'age1'}
        self.assertEquals(self.importer.cleaned_data[0], (0, content))

    def test_source_importer_file(self):
        base = BaseImporter(source=open('test.txt', 'w'))
        self.assertEqual(type(base._source), file, type(base._source))

    def test_source_importer_list(self):
        base = BaseImporter(source=['test1', 'test2'])
        self.assertEqual(type(base._source), list, type(base._source))

    def test_source_importer_django_file(self):
        class Person(models.Model):
            filefield = models.FileField(upload_to='test')

        person = Person()
        person.filefield = DjangoFile(open('test.txt', 'w'))

        base = BaseImporter(source=person.filefield)
        self.assertEqual(type(base._source), file, type(base._source))

    def test_save_data_content(self):
        for row, data in self.importer.cleaned_data:
            instace = Person(**data)
            self.assertTrue(instace.save())

    def tearDown(self):
        try:
            os.remove('test.txt')
        except:
            pass
