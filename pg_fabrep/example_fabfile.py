#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.api import env, task
from pg_fabrep.tasks import *


@task
def example_cluster():
    # name of your cluster - only numbers, letters and underscores
    env.cluster_name = 'example_cluster'

    # postgres cluster port
    # default: 5432
    #env.cluster_port = 5432

    # the IP of your master server
    env.pgmaster_ip = ''

    # user@host used by fabric to establish a ssh tunnel between the machine from where the "setup" is launched and the master server
    # default: 'root@<env.pgmaster_ip>'
    #env.pgmaster_user_host = "root@%s" % env.pgmaster_ip

    # always ask user for confirmation when run any tasks
    # default: True
    #env.ask_confirmation = True
