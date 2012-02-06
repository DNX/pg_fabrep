#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from os.path import abspath, dirname
from fabric.api import env, puts, abort, task
#from fabric.operations import sudo, settings, run
from fabric.contrib import console
#from fabric.contrib.files import upload_template

from fabric.colors import _wrap_with, green

green_bg = _wrap_with('42')
red_bg = _wrap_with('41')
pg_fabrep_path = dirname(abspath(__file__))


 #########################
## START pg_fabrep tasks ##
 #########################


@task
def setup():
    #  test configuration start
    if not test_configuration():
        if not console.confirm("Configuration test %s! Do you want to continue?" % red_bg('failed'), default=False):
            abort("Aborting at user request.")
    #  test configuration end
    if env.ask_confirmation:
        if not console.confirm("Are you sure you want to setup %s cluster?" % red_bg(env.project.upper()), default=False):
            abort("Aborting at user request.")
    puts(green_bg('Start setup...'))
    start_time = datetime.now()

#   xxx

    end_time = datetime.now()
    finish_message = '[%s] Correctly finished in %i seconds' % \
    (green_bg(end_time.strftime('%H:%M:%S')), (end_time - start_time).seconds)
    puts(finish_message)


@task
def test_configuration(verbose=True):
    errors = []
    parameters_info = []
    if 'cluster_name' not in env or not env.cluster_name:
        errors.append('Cluster name missing')
    elif verbose:
        parameters_info.append(('Cluster name', env.cluster_name))

    # print some feedback
    if errors:
        if len(errors) == 26:
            ''' all configuration missing '''
            puts('Configuration missing! Please read README.rst first or go ahead at your own risk.')
        else:
            puts('Configuration test revealed %i errors:' % len(errors))
            puts('%s\n\n* %s\n' % ('-' * 37, '\n* '.join(errors)))
            puts('-' * 40)
            puts('Please fix them or go ahead at your own risk.')
        return False
    elif verbose:
        for parameter in parameters_info:
            parameter_formatting = "'%s'" if isinstance(parameter[1], str) else "%s"
            parameter_value = parameter_formatting % parameter[1]
            puts('%s %s' % (parameter[0].ljust(27), green(parameter_value)))
    puts('Configuration tests passed!')
    return True
