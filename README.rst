.. raw:: html
    <p align="center">

.. image:: https://s3.amazonaws.com/auklet/static/auklet_python.png
    :target: https://auklet.io
    :align: center
    :width: 1000
    :alt: Auklet - Problem Solving Software for Python

.. raw:: html

    </p>

Auklet for Python
=================
.. image:: https://img.shields.io/pypi/v/auklet.svg
    :target: https://pypi.python.org/pypi/auklet
    :alt: PyPi page link -- version

.. image:: https://img.shields.io/pypi/l/auklet.svg
    :target: https://pypi.python.org/pypi/auklet
    :alt: PyPi page link -- Apache 2.0 License

.. image:: https://img.shields.io/pypi/pyversions/auklet.svg
    :target: https://pypi.python.org/pypi/auklet
    :alt: PyPi page link -- Python Versions

.. image:: https://api.codeclimate.com/v1/badges/7c2cd3bc63a70ac7fd73/maintainability
   :target: https://codeclimate.com/repos/5a54e10be3d6cb4d7d0007a8/maintainability
   :alt: Code Climate Maintainability

.. image:: https://api.codeclimate.com/v1/badges/7c2cd3bc63a70ac7fd73/test_coverage
   :target: https://codeclimate.com/repos/5a54e10be3d6cb4d7d0007a8/test_coverage
   :alt: Test Coverage


This is the official Python agent for `Auklet`_, official supports 2.7.9+ and 3.4-3.7, and
runs on most posix based operating systems (Debian, Ubuntu Core, Raspbian, QNX, etc).

Features
--------
- Automatic report of unhandled exceptions
- Automatic Function performance issue reporting
- Location, system architecture, and system metrics identification for all issues
- Ability to define data usage restriction


Compliance
----------
Auklet is an edge first application performance monitor and as such
after 1.0 releases of our packages we maintain the following compliance levels:

- Automotive Safety Integrity Level B (ASIL B)

If there are additional compliances that your industry requires please contact
the team at `hello@auklet.io`_.


Quickstart
----------

To install the agent with *pip*::

    pip install auklet

To setup Auklet monitoring for you application:

.. sourcecode:: python

    from auklet.monitoring import Monitoring
    auklet_monitoring = Monitoring("api_key", "app_id", "git_commit_hash")

    auklet_monitoring.start()
    # Call your main function
    main()
    auklet_monitoring.stop()


`git_commit_hash` is the commit hash of the commit which represents this
deployed version of your application. There are a couple ways for which to set
this based upon the style of deployment of your application.

In the case that you deploy your entire packaged github repository and have
git installed on the device you can get it via a subprocess:

.. sourcecode:: python

    git_commit_hash = subprocess.check_output(
        ['git', 'rev-parse', 'HEAD']).strip("\n")


If you package your app and deploy it without access to git and the repo's
commit history you can include it via environment variable:

.. sourcecode:: python

    git_commit_hash = os.environ.get("APPLICATION_GIT_COMMIT_HASH")


Lastly if it is difficult or impossible to set an environment variable
via your deployment platform you can include a new file in your packaged
deployment which holds the release which you can read from and supply to
the constructor.

To write the commit hash to a file:

.. sourcecode:: shell

    git rev-parse HEAD > path/to/git_commit_hash.txt

This can then be read by adding the following to your python code.

.. sourcecode:: python

    my_file = open("git_commit_hash.txt", "r")
    git_commit_hash = my_file.read()

Resources
---------
* `Auklet`_
* `Python Documentation`_
* `Issue Tracker`_

.. _Auklet: https://auklet.io
.. _hello@auklet.io: mailto:hello@auklet.io
.. _ESG-USA: https://github.com/ESG-USA
.. _ESG Organization: https://github.com/ESG-USA
.. _Python Documentation: https://docs.auklet.io/docs/python-integration
.. _Issue Tracker: https://github.com/aukletio/Auklet-Agent-Python/issues
