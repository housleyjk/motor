# Copyright 2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import shutil
import subprocess

try:
    from io import BytesIO as StringIO
except ImportError:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

pymongo_modules = ['bson', 'gridfs', 'pymongo']


def run(cmd):
    assert 0 == subprocess.call(cmd)


def remove_contents(dir_name):
    for file_name in os.listdir(dir_name):
        full_name = os.path.join(dir_name, file_name)
        if os.path.isdir(full_name):
            shutil.rmtree(full_name)
        else:
            os.remove(full_name)


def make_empty_file(file_name):
    with open(file_name, 'w+') as f:
        f.close()


# Only parses a small subset of Python's import syntax, but enough to match
# PyMongo's internal imports.
import_pat = re.compile(
    r'^(?P<indent>\s*)import (?P<module>\w+|\(.*?\))',
    re.MULTILINE | re.DOTALL)

import_from_pat = re.compile(
    r'^(?P<indent>\s*)from (?P<module>\w+)(?P<submodules>(\.\w+)*) import (?P<names>\w+|\*|\(.*?\))',
    re.MULTILINE | re.DOTALL)


def vendorize_python_imports(file_name, destination):
    print file_name

    def replace_import(match):
        indentation = match.group('indent')
        module_name = match.group('module')
        if module_name in pymongo_modules:
            return '%simport _motor_%s as %s' % (
                indentation, module_name, module_name)
        else:
            # Don't change.
            return match.group(0)

    def replace_import_from(match):
        indentation = match.group('indent')
        module_name = match.group('module')
        sub_modules = match.group('submodules')
        names = match.group('names')
        if module_name in pymongo_modules:
            return '%sfrom _motor_%s%s import %s' % (
                indentation, module_name, sub_modules, names)
        else:
            # Don't change.
            return match.group(0)

    contents = open(file_name).read()
    contents = import_pat.sub(replace_import, contents)
    contents = import_from_pat.sub(replace_import_from, contents)

    with open(destination, 'w+') as f:
        f.write(contents)


c_import_pat = re.compile(r'(PyImport_ImportModule\(")(\w+)((\.\w+)*"\))')


def vendorize_c_imports(file_name, destination):
    print file_name

    def replace_import(match):
        module_name = match.group(2)
        if module_name in pymongo_modules:
            return (
                match.group(1)
                + '_motor_%s' % module_name
                + match.group(3))
        else:
            # Don't change.
            return match.group(0)

    contents = open(file_name).read()
    contents = c_import_pat.sub(replace_import, contents)

    with open(destination, 'w+') as f:
        f.write(contents)


def create_empty_dir(dir_name):
    if os.path.exists(dir_name):
        remove_contents(dir_name)
    else:
        os.mkdir(dir_name)


def main():
    for module in pymongo_modules:
        vendorized_dir = '_motor_%s' % module
        create_empty_dir(vendorized_dir)

    print('Creating empty directory: _tmp')
    create_empty_dir('_tmp')

    try:
        run([
            'git',
            'clone',
            '--depth', '1',
            'https://github.com/mongodb/mongo-python-driver.git',
            '_tmp'])

        for file_name in os.listdir('_tmp'):
            full_name = os.path.join('_tmp', file_name)
            if os.path.isdir(full_name):
                if file_name not in pymongo_modules:
                    shutil.rmtree(full_name)
            else:
                os.remove(full_name)

        for dir_path, dir_names, file_names in os.walk('_tmp'):
            for file_name in file_names:
                full_name = os.path.join(dir_path, file_name)
                destination_dir = '_motor_' + dir_path.split(os.sep, 1)[1]
                destination = os.path.join(destination_dir, file_name)
                if file_name.endswith('.py'):
                    vendorize_python_imports(full_name, destination)

                elif file_name.endswith('.c'):
                    vendorize_c_imports(full_name, destination)

    finally:
        print('Deleting _tmp')
        shutil.rmtree('_tmp')

if __name__ == '__main__':
    main()
