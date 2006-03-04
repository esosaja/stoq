#!/usr/bin/env python
# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005, 2006 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
## USA.
##
## Author(s): Evandro Vale Miquelito    <evandro@async.com.br>
##            Rud� Porto Filgueiras     <rudazz@gmail.com>
##
""" Run all the domain test suite """

import os
import sys

from kiwi import environ
from kiwi.log import set_log_level

from stoqlib.lib.runtime import (print_immediately, get_connection,
                                 set_verbose)


DEFAULT_SEPARATORS = 79


def test_gui(options, tests=None):
    from stoqlib.lib.runtime import new_transaction

    if options.verbose:
        set_log_level('uitest', 5)
        print_immediately('Performing gui module tests... ')

    root = os.path.abspath(os.path.join(sys.argv[0], '..', '..', '..'))
    oldpwd = os.getcwd()
    os.chdir(root)

    # Running kiwi-ui tests
    if not tests:
        test_dir = os.path.abspath(os.path.join(root, 'stoq', 'tests', 'gui'))
        tests = [os.path.join(test_dir, filename)
                 for filename in os.listdir(test_dir)
                     if filename.endswith('.py') and filename[0] != '_']
    else:
        tests = [os.path.join(oldpwd, test) for test in tests]

    # Sort the tests so they're run in a predictible order
    # useful for tests which depend on others being ran before
    tests.sort()

    conn = get_connection()
    for filename in tests:
        test_name = os.path.basename(filename)
        if options.verbose:
            print 'RUNNING', test_name
            print '=' * DEFAULT_SEPARATORS
        globs = {}
        environ.app = None

        # Run each tests in a child process, since kiwis ui test framework
        # is not completely capable of cleaning up all it's state
        # seems to be highly threads related.
        pid = os.fork()
        if not pid:
            # Do thread initialization here, in the child process
            # avoids strange X errors
            from kiwi.ui.test.player import TimeOutError

            try:
                execfile(filename, globs)
            except TimeOutError, e:
                print '*' * 50
                print '* TIMEOUT ERROR: %s' % e
                print '*' * 50
                os._exit(1)
            raise SystemExit

        pid, status = os.waitpid(pid, 0)
        if status != 0:
            print '%s failed' % test_name
            return 1

        post_hook = globs.get('post_hook')
        if post_hook:
            post_hook(new_transaction())

        if options.verbose:
            print '=' * DEFAULT_SEPARATORS

    os.chdir(oldpwd)
    if options.verbose:
        print_immediately('gui tests ok')
    return 0


def main(args):
    from stoq.main import setup_environment, get_parser

    if '--g-fatal-warnings' in args:
        args.remove('--g-fatal-warnings')

    parser = get_parser()
    # Additional options only useful for tests
    parser.add_option('-v', '--verbose',
                      action="store_true",
                      dest="verbose")
    parser.add_option('-f', '--filename',
                      action="store",
                      type="string",
                      dest="filename",
                      default="stoq.conf",
                      help='Use this file name for config file')
    options, args = parser.parse_args(args)

    setup_environment(options, options.verbose, force_init_db=True,
                      test_mode=True)

    from stoqlib.domain.examples.createall import create
    set_verbose(options.verbose)
    create()
    return test_gui(options, args[1:])

if __name__ == '__main__':
    sys.exit(main(sys.argv[:]))
