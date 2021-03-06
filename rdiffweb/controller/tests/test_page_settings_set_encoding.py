#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Created on Jan 1, 2016

@author: Patrik Dufresne <info@patrikdufresne.com>
"""
from __future__ import unicode_literals

import logging
import unittest

from rdiffweb.test import WebCase


class SetEncodingTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def _settings(self, repo):
        self.getPage("/settings/" + repo + "/")

    def _set_encoding(self, repo, encoding):
        self.getPage("/settings/" + repo + "/", method="POST",
                     body={'new_encoding': encoding})

    def test_check_encoding(self):
        self._settings(self.REPO)
        self.assertInBody("Character encoding")
        self.assertInBody('selected value="utf-8"')

    def test_api_set_encoding(self):
        """
        Check if /api/set-encoding/ is still working.
        """
        self.getPage("/api/set-encoding/" + self.REPO + "/", method="POST", body={'new_encoding': 'cp1252'})
        self.assertStatus(200)
        # Check results
        user = self.app.userdb.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        self.assertEqual('cp1252', repo.encoding)

    def test_set_encoding(self):
        """
        Check to update the encoding with cp1252.
        """
        self._set_encoding(self.REPO, 'cp1252')
        self.assertStatus(200)
        self.assertInBody("Updated")
        self.assertEquals('cp1252', self.app.userdb.get_user(self.USERNAME).get_repo(self.REPO).encoding)
        # Get back encoding.
        self._settings(self.REPO)
        self.assertInBody('selected value="cp1252"')
        
    def test_set_encoding_capital_case(self):
        """
        Check to update the encoding with US-ASCII.
        """
        self._set_encoding(self.REPO, 'US-ASCII')
        self.assertStatus(200)
        self.assertInBody("Updated")
        self.assertEquals('ascii', self.app.userdb.get_user(self.USERNAME).get_repo(self.REPO).encoding)
        # Get back encoding.
        self._settings(self.REPO)
        self.assertInBody('selected value="ascii"')

    def test_set_encoding_invalid(self):
        """
        Check to update the encoding with invalid value.
        """
        self._set_encoding(self.REPO, 'invalid')
        self.assertStatus(400)
        self.assertInBody("invalid encoding value")

    def test_set_encoding_windows_1252(self):
        """
        Check to update the encoding with windows 1252.
        """
        # Update encoding
        self._set_encoding(self.REPO, 'windows_1252')
        self.assertStatus(200)
        self.assertInBody("Updated")
        # Get back encoding.
        self._settings(self.REPO)
        self.assertInBody('selected value="cp1252"')
        self.assertEquals('cp1252', self.app.userdb.get_user(self.USERNAME).get_repo(self.REPO).encoding)
        
    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = self.app.userdb.add_user('anotheruser', 'password')
        user_obj.user_root = self.app.testcases
        user_obj.repos = ['testcases']
        
        self._set_encoding('anotheruser/testcases', 'cp1252')
        self.assertStatus('200 OK')
        self.assertEquals('cp1252', user_obj.get_repo('anotheruser/testcases').encoding)
        
        # Remove admin right
        admin = self.app.userdb.get_user('admin')
        admin.is_admin = 0
        
        # Browse admin's repos
        self._set_encoding('anotheruser/testcases', 'utf-8')
        self.assertStatus('403 Forbidden')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
