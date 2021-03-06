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
Created on Apr 10, 2016

@author: Patrik Dufresne <info@patrikdufresne.com>
"""
from __future__ import unicode_literals

import logging
import unittest

from rdiffweb.test import WebCase


class DeleteRepoTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def _settings(self, repo):
        self.getPage("/settings/" + repo + "/")

    def _delete(self, repo, confirm, **kwargs):
        body = {}
        body.update({'action': 'delete'})
        if confirm is not None:
            body.update({'confirm': confirm})
        if kwargs:
            body.update(kwargs)
        self.getPage("/settings/" + repo + "/", method="POST", body=body)

    def test_delete(self):
        """
        Check to delete a repo.
        """
        self._delete(self.REPO, 'testcases')
        self.assertStatus(303)
        self.assertEqual([], self.app.userdb.get_user('admin').repos)

    def test_delete_with_slash(self):
        self.app.userdb.get_user('admin').repos = ['/testcases']
        self._delete(self.REPO, 'testcases')
        self.assertStatus(303)
        self.assertEqual([], self.app.userdb.get_user('admin').repos)

    def test_delete_wrong_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        self._delete(self.REPO, 'wrong')
        # TODO Make sure the repository is not delete
        self.assertStatus(400)
        self.assertEqual(['testcases'], self.app.userdb.get_user('admin').repos)

    def test_delete_without_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        self._delete(self.REPO, None)
        # TODO Make sure the repository is not delete
        self.assertStatus(400)
        self.assertEqual(['testcases'], self.app.userdb.get_user('admin').repos)
        
    def test_as_another_user(self):
        """
        From admin user delete anotehr user repo.
        """
        # Create a nother user with admin right
        user_obj = self.app.userdb.add_user('anotheruser', 'password')
        user_obj.user_root = self.app.testcases
        user_obj.repos = ['testcases']
        
        self._delete('anotheruser/testcases', 'testcases', redirect='/admin/repos/')
        self.assertStatus(303)
        location = self.assertHeader('Location')
        self.assertTrue(location.endswith('/admin/repos/'))
        
        # Check database update
        self.assertEqual([], user_obj.repos)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
