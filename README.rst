===========================================================================
pg_fabrep: Postgresql Streaming Replication with Fabric and Repmgr
===========================================================================

Introduction
============

pg_fabrep allow you to easy setup a **Postgresql** 9.x **Hot Standby Streaming Replication** Server With **Repmgr**.

Patches are welcome! Feel free to fork and contribute to this project on:

**bitbucket**: `bitbucket.org/DNX/pg_fabrep <https://bitbucket.org/DNX/pg_fabrep/>`_


**github**: `github.com/DNX/pg_fabrep <https://github.com/DNX/pg_fabrep>`_


Installation
============

There are a few different ways to install pg_fabrep:

Using pip
---------
If you have pip install available on your system, just type::

    pip install pg_fabrep

If you've already got an old version of pg_fabrep, and want to upgrade, use::

    pip install -U pg_fabrep

Installing from a directory
---------------------------
If you've obtained a copy of pg_fabrep using either Mercurial or a downloadable
archive, you'll need to install the copy you have system-wide. Try running::

    python setup.py develop

If that fails, you don't have ``setuptools`` or an equivalent installed;
either install them, or run::

    python setup.py install


How to use pg_fabrep?
=====================

If you have already installed pg_fabrep, you must proceed with the
configuration of your cluster.

Configuration
-------------

Copy the scheleton for your cluster settings from <pg_fabrep> path::

    $ cp <pg_fabrep>/example_fabfile.py <your_project>/fabfile.py

How to find your <pg_fabrep> path? Just run::

    $ python -c "import pg_fabrep; print(pg_fabrep.__path__)"

or directly:

    $ cp `python -c "import pg_fabrep; print(pg_fabrep.__path__[0])"`/example_fabfile.py <your_project>/fabfile.py

In order to start **setup** task you must change only two parameters,
**pgmaster_ip** and **pgslave_ip** inside you cluster configuration task in earlier created **fabfile.py**, all other parameters have default
values and if you need you can change them too.

Here is a list with all parameters you can change and a short explanation for each:

- **env.configured**, don't change this, used for testing purposes
- **env.postgres_version**, postgres version, can be: "9.0" or "9.1", default: "9.1"
- **env.cluster_name**, name of your cluster - only numbers, letters and underscores, default: main
- **env.cluster_port**, postgres cluster port, default: 5432
- **env.pgmaster_ip**, the IP of your master server
- **env.master_ssh_port**, ssh port on the master server, will be used by repmgr/rsync from the slave to sync the files from the master, default: 22
- **env.master_node_number**, master node number, default: 1
- **env.pgmaster_user_host**, user@host used by fabric to establish a ssh tunnel between the machine from where the "setup" is launched and the master server, default: "root@<env.pgmaster_ip>"
- **env.master_pgconf_path**, master pgconf path, default: "/etc/postgresql/<env.postgres_version>/<cluster_name>/"
- **env.master_pgdata_path**, master pgdata path, default: "/var/lib/postgresql/<env.postgres_version>/<env.cluster_name>/"
- **env.pgslave_ip**, the IP of your slave server
- **env.slave_node_number**, slave node number, default: 2
- **env.pgslave_user_host**, user@host used by fabric to establish a ssh tunnel between the machine from where the "setup" is launched and the slave server, default: "root@<env.pgslave_ip>"
- **env.slave_pgconf_path**, slave pgconf path, default: "<env.master_pgconf_path>"
- **env.slave_pgdata_path**, slave pgdata path, default: "<env.master_pgdata_path>"
- **env.sync_db**, sync database used by repmgr, will be created if not exists, default: "syncdb"
- **env.sync_user**, sync postgres user used by repmgr, will be created if not exists, default: "syncuser"
- **env.sync_pass**, sync postgres user password, default: "syncpass"
- **env.repmgr_deb**, repmgr_deb installer, default:"postgresql-repmgr-<env.postgres_version>_1.0.0.deb"
- **env.ask_confirmation**, always ask user for confirmation when run any tasks, default: True


Please pay attention to not have any tasks in your fabfile.py called:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

* setup

* test_configuration

or

* print_configuration

because these names are reserved by pg_fabrep.

Test your configuration first!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pg_fabrep come with its own automatic configuration tests. Each time you run
**setup** task, configuration tests are called.
Anyway, you can manually run these tests for your project configuration::

    fab <cluster_task_name> test_configuration

If you run **test_configuration** manually, you'll observe some output about all your project settings.

Do you need an example?
~~~~~~~~~~~~~~~~~~~~~~~

Ok, let's assume you want to configure a cluster called "cluster5444".
So, what we know about it?
we know:

* the cluster is called **cluster123**

* the postgres version we want to be used is 9.1

* the ip of the master server is: **11.11.11.11**

* the ip of the slave server is: **22.22.22.22**

* the port to be used in your cluster is 5444

* on each server is installed ubuntu server

Ok, it's enough to setup the replication, let's do it!
Create a folder to place you cluster settings::

    $ mkdir ~/clusters/
    $ cd ~/clusters/

copy here the example_fabfile.py from <pg_fabrep>::

    # we found pg_fabrep installation path first
    $ python -c "import pg_fabrep; print(pg_fabrep.__path__)"
    $ cp <pg_fabrep>/example_fabfile.py fabfile.py

now, in our current folder we have a file called **fabfile.py**
which is going to be edited according with our needs.

#. Change task name::

    # from:
    def example_cluster():
    # to:
    def cluster123():

#. Change env.pgmaster_ip::

    # from:
    env.pgmaster_ip = ""
    # to:
    env.pgmaster_ip = "11.11.11.11"

#. Change env.pgslave_ip::

    # from:
    env.pgslave_ip = ""
    # to:
    env.pgslave_ip = "22.22.22.22"

not, let's test our configuration::

    fab cluster123 test_configuration

you must see a message::

    Configuration tests passed!


Setup your replication
----------------------

Assuming you've set your cluster details in the fabfile.py now you are ready to launch the setup::

    fab cluster123 setup

during this process you can see all the output of the commands launched on
the master and slave servers. At some point you may be asked for some
information as sudo user password.
At the end of this task you must view a message saying that the setup
successful ended.
Now you can go on with the real tests of the replication.