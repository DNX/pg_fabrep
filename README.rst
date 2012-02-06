===========================================================================
pg_fabrep: Postgresql Streaming Replication with Fabric and Repmgr
===========================================================================

Introduction
============

pg_fabrep allow you to easy setup a Postgresql 9.x Hot Standby Streaming Replication Server With Repmgr.

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

to do...

Please pay attention to not have any tasks in your fabfile.py called:
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

* setup

* deploy

* test_configuration

or

* hg_pull

because these names are reserved by pg_fabrep.

Test your configuration first!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
pg_fabrep come with its own automatic configuration tests. Each time you run
**setup** or **deploy** task, configuration tests are called.
Anyway, you can manually run these tests for your project configuration::

    fab cluster_name test_configuration

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

!!! TO DO: add another info


Ok, it's enough to setup the replication, let's do it!
Clone postgres_replication skeleton::

    cp path/to/your/workspace/

or::

    hg clone https://bitbucket.org/DNX/postgres_replication/


Now apply some changes to earlier cloned folder:

* in the fabfile.py::

    # to be added...

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