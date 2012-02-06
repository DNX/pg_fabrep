#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fabric.api import env, task
from pg_fabrep.tasks import *


@task
def example_cluster():
    #  name of your cluster - no spaces, no special chars
    env.cluster_name = 'example_cluster'
    #  always ask user for confirmation when run any tasks
    #  default: True
    #env.ask_confirmation = True
