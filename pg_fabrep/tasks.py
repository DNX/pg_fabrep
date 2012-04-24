#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from os.path import abspath, dirname, isfile
from datetime import datetime
from fabric.api import env, puts, abort, task, put, hide, cd
from fabric.operations import sudo, settings, run
from fabric.contrib import console
from fabric.contrib.files import upload_template

from fabric.colors import _wrap_with, green, red

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

    # Start configuring master server
    with settings(host_string=env.pgmaster_user_host):
        print "%s configuring master server!" % green_bg("Start")
        _verify_sudo()
        _common_setup()
        with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
            res = sudo("pg_createcluster --start %(postgres_version)s %(cluster_name)s -p %(cluster_port)s" % env)
        if 'already exists' in res:
            puts(green("Cluster '%(cluster_name)s' already exists, will not be changed." % env))
        if 'Error: port %s is already used' % env.cluster_port in res:
            puts(red(res))
        with cd(env.master_pgdata_path):
            with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
                run('''sudo -u postgres psql -p %(cluster_port)s -c "CREATE USER %(sync_user)s SUPERUSER ENCRYPTED PASSWORD '%(sync_pass)s';"''' % env, shell=False)
                run('''sudo -u postgres createdb -p %(cluster_port)s --owner %(sync_user)s --template template0 --encoding=UTF8 --lc-ctype=en_US.UTF-8 --lc-collate=en_US.UTF-8 %(sync_db)s''' % env, shell=False)
                run('''sudo -u postgres psql -p %(cluster_port)s -c "GRANT CREATE, CONNECT ON DATABASE %(sync_db)s TO %(sync_user)s WITH GRANT OPTION;"''' % env, shell=False)
        postgres_conf_file = 'conf/postgres/postgresql.conf'
        if not isfile(postgres_conf_file):
            postgres_conf_file = '%s/%s' % (pg_fabrep_path, postgres_conf_file)
        upload_template(postgres_conf_file, env.master_pgconf_path,
                            context=env, backup=False)
        if env.verbose:
            puts("Uploaded postgresql.conf from %s to %s" % (green(abspath(postgres_conf_file)), green(env.master_pgconf_path)))
        # start preparing pg_hba.conf file
        replication_hba = '%sreplication_hba.conf' % env.master_pgconf_path
        pg_hba = '%spg_hba.conf' % env.master_pgconf_path
        pg_hba_bck = '%spg_hba.conf.bck' % env.master_pgconf_path
        pg_hba_file = 'conf/postgres/pg_hba.conf'
        if not isfile(pg_hba_file):
            pg_hba_file = '%s/%s' % (pg_fabrep_path, pg_hba_file)
        upload_template(pg_hba_file, replication_hba,
                        context=env, backup=False)
        sudo('mv %s %s' % (pg_hba, pg_hba_bck))
        sudo("sed -n -e '/START REPLICATION RULES/,/END REPLICATION RULES/!p' %s > %s" % (pg_hba_bck, pg_hba))
        sudo("cat %s >> %s" % (replication_hba, pg_hba))
        sudo("rm %s" % replication_hba)
        # upload repmgr.conf on master server
        repmgr_context = dict(cluster_name=env.cluster_name,
                              node_number=env.master_node_number,
                              sync_user=env.sync_user,
                              sync_db=env.sync_db,
                              sync_pass=env.sync_pass,
                              ssh_port=22,  # we don't need here
                              )
        repmgr_conf_file = 'conf/repmgr/repmgr.conf'
        if not isfile(repmgr_conf_file):
            repmgr_conf_file = '%s/%s' % (pg_fabrep_path, repmgr_conf_file)
        upload_template(repmgr_conf_file, env.master_pgdata_path,
                        context=repmgr_context, backup=False)
        sudo("""echo -e "# Added by pg_fabrep\nexport PGDATA='/var/lib/postgresql/%(postgres_version)s/%(cluster_name)s'\nexport PGPORT=%(cluster_port)s">/var/lib/postgresql/.bash_profile""" % env)
        sudo("pg_ctlcluster %(postgres_version)s %(cluster_name)s restart" % env)

    # Start configuring the slave
    with settings(host_string=env.pgslave_user_host):
        print "%s configuring slave server!" % green_bg("Start")
        _verify_sudo()
        _common_setup()
        sudo('rm -rf %s' % env.slave_pgdata_path)
        sudo('mkdir -p %s' % env.slave_pgdata_path)
        sudo('chown postgres:postgres %s' % env.slave_pgdata_path)
        _standby_clone()
        finish_configuring_slave()  # you can start it manually

    #  TODO: ...
    # # repmgr register master
    # with settings(host_string=env.master_host_local_ip):
    #     sudo('repmgr -f %srepmgr.conf --verbose master register' % \
    #          env.master_pgdata_path, user='postgres')
    # # repmgr register slave
    # with settings(host_string=env.slave_host):
    #     sudo('repmgr -f %srepmgr.conf --verbose standby register' % \
    #          env.slave_pgdata_path, user='postgres')
    end_time = datetime.now()
    finish_message = '[%s] Correctly finished in %i seconds' % \
    (green(end_time.strftime('%H:%M:%S')), (end_time - start_time).seconds)
    puts(finish_message)


@task
def test_configuration():
    errors = []
    if not env.get('configured'):
        puts(red('Configuration missing! Please read README.rst first or go ahead at your own risk.'))
        return False

    supported_postgres_versions = ("9.0", "9.1")
    if not env.postgres_version:
        errors.append('Postgres version missing')
    elif env.postgres_version not in supported_postgres_versions:
        errors.append('Wrong postgres version, supported versions are: "%s"' % '", "'.join(supported_postgres_versions))
    if not env.cluster_name:
        errors.append('Cluster name missing')
    elif not re.search(r"^\w+$", env.cluster_name):
        errors.append("%s is not a valid app name. Please use only numbers, letters and underscores." % red_bg(env.cluster_name))

    if not env.get('pgmaster_ip'):
        errors.append('Master server IP missing')
    if not env.get('master_ssh_port'):
        errors.append('Master server ssh port missing')
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
    if not env.get('repmgr_deb'):
        errors.append('Repmgr deb file path missing')

    # print some feedback
    if errors:
        puts(red('Configuration test revealed %i errors:' % len(errors)))
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
    parameters_info.append(("Postgres version", env.postgres_version))
    parameters_info.append(("Cluster name", env.cluster_name))
    parameters_info.append(("Cluster port", env.cluster_port))
    parameters_info.append(("--- Master Configuration", "----------"))
    parameters_info.append(("Master server IP", env.pgmaster_ip))
    parameters_info.append(("Master server ssh port", env.master_ssh_port))
    parameters_info.append(("Master node number", env.master_node_number))
    parameters_info.append(("Master user@host", env.pgmaster_user_host))
    parameters_info.append(("Master pgconf path", env.master_pgconf_path))
    parameters_info.append(("Master pgdata path", env.master_pgdata_path))
    parameters_info.append(("--- Slave Configuration", "----------"))
    parameters_info.append(("Slave server IP", env.pgslave_ip))
    parameters_info.append(("Slave node number", env.slave_node_number))
    parameters_info.append(("Slave user@host", env.pgslave_user_host))
    parameters_info.append(("Slave pgconf path", env.slave_pgconf_path))
    parameters_info.append(("Slave pgdata path", env.slave_pgdata_path))
    parameters_info.append(("--- Repmgr Configuration", "----------"))
    parameters_info.append(("Sync database name", env.sync_db))
    parameters_info.append(("Sync user", env.sync_user))
    parameters_info.append(("Sync password", env.sync_pass))
    parameters_info.append(("Repmgr deb file path", env.repmgr_deb))

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
    if 'pgmaster_ip' not in env:
        env.pgmaster_ip = ''
    if 'master_ssh_port' not in env:
        env.master_ssh_port = 22
    if 'master_node_number' not in env:
        env.master_node_number = 1
    if 'pgmaster_user_host' not in env:
        env.pgmaster_user_host = "root@%s" % env.pgmaster_ip
    if 'master_pgconf_path' not in env:
        env.master_pgconf_path = '/etc/postgresql/%s/%s/' % (env.postgres_version, env.cluster_name)
    if 'master_pgdata_path' not in env:
        env.master_pgdata_path = '/var/lib/postgresql/%s/%s/' % (env.postgres_version, env.cluster_name)
    if 'pgslave_ip' not in env:
        env.pgslave_ip = ''
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
    if 'repmgr_deb' not in env:
        env.repmgr_deb = "postgresql-repmgr-%s_1.0.0.deb" % env.postgres_version
    if 'ask_confirmation' not in env:
        env.ask_confirmation = True
    if 'verbose' not in env:
        env.verbose = False


@task
def finish_configuring_slave():
    parameter_default_values()
    with settings(host_string=env.pgslave_user_host):
        # upload repmgr.conf on slave server
        repmgr_context = dict(cluster_name=env.cluster_name,
                              node_number=env.slave_node_number,
                              sync_user=env.sync_user,
                              sync_db=env.sync_db,
                              sync_pass=env.sync_pass,
                              ssh_port=env.master_ssh_port,
                              )
        repmgr_conf_file = 'conf/repmgr/repmgr.conf'
        if not isfile(repmgr_conf_file):
            repmgr_conf_file = '%s/%s' % (pg_fabrep_path, repmgr_conf_file)
        upload_template(repmgr_conf_file, env.master_pgdata_path,
                        context=repmgr_context, backup=False)
        slave_postgresql_conf = "%spostgresql.conf" % env.slave_pgdata_path
        slave_postgresql_conf_bck = "%spostgresql.conf.bck" % env.slave_pgdata_path
        sudo('mv %s %s' % (slave_postgresql_conf, slave_postgresql_conf_bck))
        sudo("sed '/hot_standby =/c hot_standby = on' %s > %s" % \
             (slave_postgresql_conf_bck, slave_postgresql_conf))
        sudo("mkdir -p %s" % env.slave_pgconf_path)
        sudo("cp %spg_hba.conf %s" % (env.slave_pgdata_path, env.slave_pgconf_path))
        sudo("cp %spg_ident.conf %s" % (env.slave_pgdata_path, env.slave_pgconf_path))
        sudo("cp %spostgresql.conf %s" % (env.slave_pgdata_path, env.slave_pgconf_path))
        run("sudo -u postgres pg_ctl -D /var/lib/postgresql/%(postgres_version)s/%(cluster_name)s/ start" % env)


def _verify_sudo():
    ''' we just check if the user is sudoers '''
    sudo('cd .')


def _add_postgres9_ppa():
    ''' add postgresql 9.x ppa '''
    sudo('add-apt-repository ppa:pitti/postgresql')


def _install_dependencies():
    ''' Ensure those Debian/Ubuntu packages are installed '''
    packages = [
        'postgresql-%s' % env.postgres_version,
        'libpq-dev',
        'postgresql-server-dev-%s' % env.postgres_version,
        'postgresql-contrib-%s' % env.postgres_version,
        'libxslt-dev',
        'libxml2-dev',
        'libpam-dev',
        'libedit-dev',
    ]
    sudo("apt-get update")
    sudo("apt-get -y install %s" % " ".join(packages))
    #sudo("pip install --upgrade pip")


def _common_setup():
    sudo("apt-get -y install python-software-properties")
    _add_postgres9_ppa()
    _install_dependencies()
    # create a symlink in /usr/bin/ for /usr/lib/postgresql/<postgres_version>/bin/pg_ctl
    sudo('ln -sf /usr/lib/postgresql/%s/bin/pg_ctl /usr/bin/' % env.postgres_version)
    # install repmgr
    remote_repmgr_deb = '/tmp/%s' % env.repmgr_deb
    if isfile(env.repmgr_deb):
        local_repmgr_deb = env.repmgr_deb
    else:
        local_repmgr_deb = '%s/deb/%s' % (pg_fabrep_path, env.repmgr_deb)
    put(local_repmgr_deb, remote_repmgr_deb)
    run('dpkg -i --force-overwrite %s' % remote_repmgr_deb)
    sudo("rm %s" % remote_repmgr_deb)


def _standby_clone():
    """ With "node1" server running, we want to use the clone standby
    command in repmgr to copy over the entire PostgreSQL database cluster
    onto the "node2" server. """
    # manualy:
    # $ mkdir -p /var/lib/postgresql/9.1/testscluster/
    # $ rsync -avz --rsh='ssh -p2222' root@12.34.56.789:/var/lib/postgresql/9.1/testscluster/ /var/lib/postgresql/9.1/testscluster/

    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        puts(green('Start cloning the master'))
        repmgr_clone_command = 'repmgr -D %(slave_pgdata_path)s -d %(sync_db)s -p %(cluster_port)s -U %(sync_user)s -R postgres --verbose standby clone %(pgmaster_ip)s' % env
        puts(green(repmgr_clone_command))
        puts("-" * 40)
        res = sudo(repmgr_clone_command, user='postgres')
        if 'Can not connect to the remote host' in res or 'Connection to database failed' in res:
            puts("-" * 40)
            puts(green(repmgr_clone_command))
            puts("-" * 40)
            puts("Master server is %s reachable." % red("NOT"))
            puts("%s you can try to CLONE the slave manually [%s]:" % (green("BUT"), red("at your own risk")))
            puts("On the slave server:")
            puts("$ sudo -u postgres rsync -avz --rsh='ssh -p%(master_ssh_port)s' postgres@%(pgmaster_ip)s:%(master_pgdata_path)s %(slave_pgdata_path)s --exclude=pg_xlog* --exclude=pg_control --exclude=*.pid" % env)
            puts("Here:")
            puts("$ fab <cluster_task_name> finish_configuring_slave")
            abort("STOP...")
