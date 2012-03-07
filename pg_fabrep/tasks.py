#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from os.path import abspath, dirname
from datetime import datetime
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
    parameter_default_values()
    #  test configuration start
    if not test_configuration():
        if not console.confirm("Configuration test %s! Do you want to continue?" % red_bg('failed'), default=False):
            abort("Aborting at user request.")
    #  test configuration end
    if env.ask_confirmation:
        if not console.confirm("Are you sure you want to setup %s cluster?" % green(env.cluster_name.upper()), default=False):
            abort("Aborting at user request.")
    puts(green_bg('Start setup...'))
    start_time = datetime.now()

#   xxx

    end_time = datetime.now()
    finish_message = '[%s] Correctly finished in %i seconds' % \
    (green_bg(end_time.strftime('%H:%M:%S')), (end_time - start_time).seconds)
    puts(finish_message)


@task
def test_configuration():
    errors = []

    if not env.postgres_version:
        errors.append('Postgres version missing')
    if not env.cluster_name:
        errors.append('Cluster name missing')
    elif not re.search(r"^\w+$", env.cluster_name):
        errors.append("%s is not a valid app name. Please use only numbers, letters and underscores." % red_bg(env.cluster_name))

    if not env.get('pgmaster_ip'):
        errors.append('Master server IP missing')
    if not env.get('master_node_number'):
        errors.append('Incorrect master node number')
    if not env.get('pgmaster_user_host'):
        errors.append('Incorrect master user@host')
    if not env.get('master_pgconf_path'):
        errors.append('Incorrect master pgconf path')
    if not env.get('master_pgdata_path'):
        errors.append('Incorrect master pgdata path')
    if not env.get('pgslave_ip'):
        errors.append('Slave server IP missing')
    if not env.get('slave_node_number'):
        errors.append('Incorrect slave node number')
    if not env.get('pgslave_user_host'):
        errors.append('Incorrect slave user@host')
    if not env.get('slave_pgconf_path'):
        errors.append('Incorrect slave pgconf path')
    if not env.get('slave_pgdata_path'):
        errors.append('Incorrect slave pgdata path')
    if not env.get('sync_db'):
        errors.append('Sync database name missing')
    if not env.get('sync_user'):
        errors.append('Sync user missing')
    if not env.get('sync_pass'):
        errors.append('Sync password missing')

    # print some feedback
    if errors:
        puts('Configuration test revealed %i errors:' % len(errors))
        puts('%s\n\n* %s\n' % ('-' * 37, '\n* '.join(errors)))
        puts('-' * 40)
        puts('Please fix them or go ahead at your own risk.')
        return False
    puts(green('Configuration tests passed!'))
    print_configuration()
    return True


@task
def print_configuration():
    parameters_info = []
    parameters_info.append(('Postgres version', env.postgres_version))
    parameters_info.append(('Cluster name', env.cluster_name))
    parameters_info.append(('Cluster port', env.cluster_port))
    parameters_info.append(('--- Master Configuration', '----------'))
    parameters_info.append(('Master server IP', env.pgmaster_ip))
    parameters_info.append(('Master node number', env.master_node_number))
    parameters_info.append(('Master user@host', env.pgmaster_user_host))
    parameters_info.append(('Master pgconf path', env.master_pgconf_path))
    parameters_info.append(('Master pgdata path', env.master_pgdata_path))
    parameters_info.append(('--- Slave Configuration', '----------'))
    parameters_info.append(('Slave server IP', env.pgslave_ip))
    parameters_info.append(('Slave node number', env.slave_node_number))
    parameters_info.append(('Slave user@host', env.pgslave_user_host))
    parameters_info.append(('Slave pgconf path', env.slave_pgconf_path))
    parameters_info.append(('Slave pgdata path', env.slave_pgdata_path))
    parameters_info.append(('--- Repmgr Configuration', '----------'))
    parameters_info.append(('Sync database name', env.sync_db))
    parameters_info.append(('Sync user', env.sync_user))
    parameters_info.append(('Sync password', env.sync_pass))

    # print collected info
    puts('========== START YOUR CONFIGURATION ============')
    for parameter in parameters_info:
        parameter_formatting = "'%s'" if isinstance(parameter[1], str) else "%s"
        parameter_value = parameter_formatting % parameter[1]
        puts('%s %s' % (parameter[0].ljust(27), green(parameter_value)))
    puts('========== END YOUR CONFIGURATION ==============')


def parameter_default_values():
    if 'postgres_version' not in env:
        env.postgres_version = '9.1'
    if 'cluster_name' not in env:
        env.cluster_name = 'main'
    if 'cluster_port' not in env:
        env.cluster_port = 5432
    if 'ask_confirmation' not in env:
        env.ask_confirmation = True
    if 'master_node_number' not in env:
        env.master_node_number = 1
    if 'pgmaster_user_host' not in env:
        env.pgmaster_user_host = "root@%s" % env.pgmaster_ip
    if 'master_pgconf_path' not in env:
        env.master_pgconf_path = '/etc/postgresql/%s/%s/' % (env.postgres_version, env.cluster_name)
    if 'master_pgdata_path' not in env:
        env.master_pgdata_path = '/var/lib/postgresql/%s/%s/' % (env.postgres_version, env.cluster_name)
    if 'slave_node_number' not in env:
        env.slave_node_number = 2
    if 'pgslave_user_host' not in env:
        env.pgslave_user_host = "root@%s" % env.pgslave_ip
    if 'slave_pgconf_path' not in env:
        env.slave_pgconf_path = env.master_pgconf_path
    if 'slave_pgdata_path' not in env:
        env.slave_pgdata_path = env.master_pgdata_path
    if 'sync_db' not in env:
        env.sync_db = 'syncdb'
    if 'sync_user' not in env:
        env.sync_user = 'syncuser'
    if 'sync_pass' not in env:
        env.sync_pass = 'syncpass'
