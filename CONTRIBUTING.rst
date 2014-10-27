Contributing
============================

#. **Please sign one of the contributor license agreements below.**
#. Fork the repo, develop and test your code changes, add docs.
#. Make sure that your commit messages clearly describe the changes. 
#. Send a pull request.

Here are some guidelines for hacking on gcloud-python-expenses-demo.

Using a Development Checkout
----------------------------

You'll have to create a development environment to hack on
gcloud-python-expenses-demo, using a Git checkout:

- While logged into your GitHub account, navigate to the
  gcloud-python-expenses-demo repo on GitHub.
  
  https://github.com/GoogleCloudPlatform/gcloud-python-expenses-demo

- Fork and clone the gcloud-python-expenses-demo repository to your GitHub account by
  clicking the "Fork" button.

- Clone your fork of gcloud-python-expenses-demo from your GitHub account
  to your local computer, substituting your account username and specifying
  the destination as "hack-on-gcloud".  E.g.::

   $ cd ~
   $ git clone git@github.com:USERNAME/gcloud-python-expenses-demo.git hack-on-gcloud
   $ cd hack-on-gcloud
   # Configure remotes such that you can pull changes from the gcloud-python-expenses-demo
   # repository into your local repository.
   $ git remote add upstream https://github.com:GoogleCloudPlatform/gcloud-python-expenses-demo
   # fetch and merge changes from upstream into master
   $ git fetch upstream
   $ git merge upstream/master

Now your local repo is set up such that you will push changes to your GitHub
repo, from which you can submit a pull request.

- Create a virtualenv in which to install gcloud-python-expenses-demo::

   $ cd ~/hack-on-gcloud
   $ virtualenv -ppython2.7 env

  Note that very old versions of virtualenv (virtualenv versions below, say,
  1.10 or thereabouts) require you to pass a ``--no-site-packages`` flag to
  get a completely isolated environment.

  You can choose which Python version you want to use by passing a ``-p``
  flag to ``virtualenv``.  For example, ``virtualenv -ppython2.7``
  chooses the Python 2.7 interpreter to be installed.

  From here on in within these instructions, the ``~/hack-on-gcloud/env``
  virtual environment you created above will be referred to as ``$VENV``.
  To use the instructions in the steps that follow literally, use the
  ``export VENV=~/hack-on-gcloud/env`` command.

- Install gcloud-python-expenses-demo from the checkout into the virtualenv
  using ``setup.py develop``.  Running ``setup.py develop`` *must* be done
  while the current working directory is the ``gcloud-python-expenses-demo``
  checkout directory::

   $ cd ~/hack-on-gcloud
   $ $VENV/bin/python-expenses-demo setup.py develop

I'm getting weird errors... Can you help?
-----------------------------------------

Chances are you have some dependency problems...
If you're on Ubuntu,
try installing the pre-compiled packages::

  $ sudo apt-get install python-crypto python-openssl libffi-dev

or try installing the development packages
(that have the header files included)
and then ``pip install`` the dependencies again::

  $ sudo apt-get install python-dev libssl-dev libffi-dev
  $ pip install gcloud

Adding Features
---------------

In order to add a feature to gcloud-python-expenses-demo:

- The feature must be documented in both the API and narrative
  documentation (in ``docs/``).

- The feature must work fully on the following CPython versions: 2.6,
  and 2.7 on both UNIX and Windows.

- The feature must not add unnecessary dependencies (where
  "unnecessary" is of course subjective, but new dependencies should
  be discussed).

Documentation Coverage and Building HTML Documentation
------------------------------------------------------

If you fix a bug, and the bug requires an API or behavior modification, all
documentation in this package which references that API or behavior must be
changed to reflect the bug fix, ideally in the same commit that fixes the bug
or adds the feature.

To build and review docs (where ``$VENV`` refers to the virtualenv you're
using to develop gcloud-python-expenses-demo):

1. After following the steps above in "Using a Development Checkout", install
   Sphinx and all development requirements in your virtualenv::

     $ cd ~/hack-on-gcloud
     $ $VENV/bin/pip install Sphinx

2. Change into the ``docs`` directory within your gcloud-python-expenses-demo
   checkout and execute the ``make`` command with some flags::

     $ cd ~/hack-on-gcloud/gcloud-python-expenses-demo/docs
     $ make clean html SPHINXBUILD=$VENV/bin/sphinx-build

   The ``SPHINXBUILD=...`` argument tells Sphinx to use the virtualenv Python,
   which will have both Sphinx and gcloud-python-expenses-demo (for API
   documentation generation) installed.

3. Open the ``docs/_build/html/index.html`` file to see the resulting HTML
   rendering.

Contributor License Agreements
------------------------------

Before we can accept your pull requests you'll need to sign a Contributor License Agreement (CLA):

- **If you are an individual writing original source code** and **you own the intellectual property**, then you'll need to sign an `individual CLA <https://developers.google.com/open-source/cla/individual>`__.
- **If you work for a company that wants to allow you to contribute your work**, then you'll need to sign a `corporate CLA <https://developers.google.com/open-source/cla/corporate>`__.

You can sign these electronically (just scroll to the bottom). After that, we'll be able to accept your pull requests.
