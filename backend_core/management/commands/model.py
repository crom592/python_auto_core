from django.core.management.base import BaseCommand
from django.db import models
from django.conf import settings
from rest_api.urls import load_models
import importlib
import re
import os

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        body = 'import { Model } from "@juice/frontend-core";\n\n'
        for model_name, model_class in load_models().items():
            body += self.make_type(model_name, model_class)

        os.makedirs(os.path.dirname(settings.API_MODELS_D_TS), exist_ok=True)
        with open(settings.API_MODELS_D_TS, 'w') as f:
            f.write(body)

    def make_type(self, model_name, model_class):
        parts = re.findall('[A-Z][^A-Z]*',model_name)
        path = r'%s'%'/'.join(parts).lower()

        properties = {}
        generic = []
        def get_ref(field, generic):
            val = str(field.field.target_field).split('.')[1]
            if val in generic:
                index = 0
                while True:
                    index += 1
                    if not f'{val}_{index}' in generic:
                        return f'{val}_{index}'
            return val

        for key in dir(model_class):
            if key.startswith('_'): continue
            if key.endswith('_set'): continue
            field = getattr(model_class, key)
            if hasattr(field, 'field'):
                klass = field.field.__class__
                if klass  == models.AutoField:                  type = 'number'
                elif klass == models.BigAutoField:              type = 'number'
                elif klass == models.BigIntegerField:           type = 'number'
                elif klass == models.BinaryField:               type = 'String'
                elif klass == models.BooleanField:              type = 'boolean'
                elif klass == models.CharField:                 type = 'string'
                elif klass == models.DateField:                 type = 'string'
                elif klass == models.DateTimeField:             type = 'string'
                elif klass == models.DecimalField:              type = 'number'
                elif klass == models.DurationField:             type = 'string'
                elif klass == models.EmailField:                type = 'string'
                elif klass == models.FileField:                 type = 'string'
                elif klass == models.FilePathField:             type = 'string'
                elif klass == models.FloatField:                type = 'string'
                elif klass == models.GeneratedField:            type = 'string'
                elif klass == models.GenericIPAddressField:     type = 'string'
                elif klass == models.ImageField:                type = 'string'
                elif klass == models.IntegerField:              type = 'number'
                elif klass == models.JSONField:                 type = 'string'
                elif klass == models.PositiveBigIntegerField:   type = 'number'
                elif klass == models.PositiveIntegerField:      type = 'number'
                elif klass == models.PositiveSmallIntegerField: type = 'number'
                elif klass == models.SlugField:                 type = 'number'
                elif klass == models.SmallAutoField:            type = 'number'
                elif klass == models.SmallIntegerField:         type = 'number'
                elif klass == models.TextField:                 type = 'string'
                elif klass == models.TimeField:                 type = 'string'
                elif klass == models.URLField:                  type = 'string'
                elif klass == models.UUIDField:                 type = 'string'
                elif klass == models.OneToOneField:
                    if key.endswith('_id'): continue
                    ref = get_ref(field, generic)
                    type = ref
                    generic.append(ref)
                elif klass == models.ForeignKey:
                    if key.endswith('_id'): continue
                    ref = get_ref(field, generic)
                    type = ref
                    generic.append(ref)
                elif klass == models.ManyToManyField:
                    ref = get_ref(field, generic)
                    type = f'{ref}[]'
                    generic.append(ref)
                else: continue
                required = True
                if field.field.null or field.field.default != models.fields.NOT_PROVIDED:
                    required = False
                properties[key] = {
                    'type':type,
                    'required':required
                }

        content = f'export class {model_name}'
        if len(generic) != 0:
            content += '<'
            content += ','.join(list(map(lambda d:d+'=number', generic)))
            content += '>'
        content += ' extends Model ' + '{\n'
        content += f'    static readonly API = \'/api/{path}/\'\n'
        for key, value in properties.items():
            content += f'    {key}{"!" if value["required"] else "?"}: {value["type"]}\n'
        content += '}\n'
        
        return content