# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import textwrap

# work with both pep8 and pycodestyle
try:
    import pycodestyle
except ImportError:
    import pep8 as pycodestyle
import testtools

from keystoneclient.tests.hacking import checks
from keystoneclient.tests.unit import client_fixtures


class TestCheckOsloNamespaceImports(testtools.TestCase):
    def setUp(self):
        super(TestCheckOsloNamespaceImports, self).setUp()
        self.useFixture(client_fixtures.Deprecations())

    def run_check(self, code):
        pycodestyle.register_check(checks.check_oslo_namespace_imports)

        lines = textwrap.dedent(code).strip().splitlines(True)

        guide = pycodestyle.StyleGuide(select='K333')
        checker = pycodestyle.Checker(lines=lines, options=guide.options)
        checker.check_all()
        checker.report._deferred_print.sort()
        return checker.report._deferred_print

    def assert_has_errors(self, code, expected_errors=None):
        actual_errors = [e[:3] for e in self.run_check(code)]
        self.assertEqual(expected_errors or [], actual_errors)

    def test(self):
        code_ex = self.useFixture(client_fixtures.HackingCode())
        code = code_ex.oslo_namespace_imports['code']
        errors = code_ex.oslo_namespace_imports['expected_errors']
        self.assert_has_errors(code, expected_errors=errors)
