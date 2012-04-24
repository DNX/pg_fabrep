#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.api import env, task
from pg_fabrep.tasks import *


@task
def example_cluster():
    env.configured = True  # don't change this, used for testing purposes
    # postgres version, can be: "9.0" or "9.1"
    # default: "9.1"
    #env.postgres_version = "9.1"

    # name of your cluster - only numbers, letters and underscores
    # default: main
    env.cluster_name = "main"

    # postgres cluster port
    # default: 5432
    #env.cluster_port = 5432

    # the IP of your master server
    env.pgmaster_ip = ""

    # master ssh port, will be used by repmgr/rsync from the slave to replicate the master
    # default: 22
    #env.master_ssh_port = 22

    # master node number
    # default: 1
    #env.master_node_number = 1

    # user@host used by fabric to establish a ssh tunnel between the machine from where the "setup" is launched and the master server
    # default: "root@<env.pgmaster_ip>"
    #env.pgmaster_user_host = "root@%s" % env.pgmaster_ip

    # master pgconf path
    # default: "/etc/postgresql/<env.postgres_version>/<cluster_name>/"
    #env.master_pgconf_path = "/etc/postgresql/%s/%s/" % (env.postgres_version, env.cluster_name)

    # master pgdata path
    # default: "/var/lib/postgresql/<env.postgres_version>/<env.cluster_name>/"
    #env.master_pgdata_path = "/var/lib/postgresql/%s/%s/" % (env.postgres_version, env.cluster_name)

    # the IP of your slave server
    env.pgslave_ip = ""

    # slave node number
    # default: 2
    #env.slave_node_number = 2

    # user@host used by fabric to establish a ssh tunnel between the machine from where the "setup" is launched and the slave server
    # default: "root@<env.pgslave_ip>"
    #env.pgslave_user_host = "root@%s" % env.pgslave_ip

    # slave pgconf path
    # default: "<env.master_pgconf_path>"
    #env.slave_pgconf_path = env.master_pgconf_path

    # slave pgdata path
    # default: "<env.master_pgdata_path>"
    #env.slave_pgdata_path = env.master_pgdata_path

    # sync database used by repmgr, will be created if not exists
    # default: "syncdb"
    #env.sync_db = "syncdb"

    # sync postgres user used by repmgr, will be created if not exists
    # default: "syncuser"
    #env.sync_user = "syncuser"

    # sync postgres user password
    # default: "syncpass"
    #env.sync_pass = "syncpass"

    # repmgr_deb
    # default:"postgresql-repmgr-<env.postgres_version>_1.0.0.deb"
    #env.repmgr_deb = "postgresql-repmgr-%s_1.0.0.deb" % env.postgres_version

    # always ask user for confirmation when run any tasks
    # default: True
    #env.ask_confirmation = False

    # verbose, if True will print some info during the setup
    # default: False
    #env.verbose = True
