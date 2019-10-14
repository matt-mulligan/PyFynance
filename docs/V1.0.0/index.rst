======================================
PyFynance - Personal Pythonic Finance!
======================================
PyFynance is a pythonic personal finance tool to help you track, categorise and analyse your spending habits.

|

Getting Started with PyFynance in 3 steps
=========================================
To start using PyFynance simple do the following

1) Clone the `PyFynance Repository <https://github.com/matt-mulligan/PyFynance>`_ to your local machine

|

2) Install the environment manager `pipenv <https://pypi.org/project/pipenv/>`_ if not already installed using the pip tool

.. code-block:: bash

        pip install pipenv

|

3) cd to the directory where PyFynance has been cloned and install the virtual environment with pipenv

.. code-block:: bash

        cd /path/to/PyFynance
        pipenv install

|

And you're done! PyFynance is ready to use! Check out the PyFynance Tasks Section for what PyFynance can do:


PyFynance Tasks
===============
Tasks are the basic building block of PyFynance. A task is a unit of functionality that PyFynance can do for you.

As PyFynance is a command line tool, all tasks are triggered from the command line using the --task_type flag

|

See below the list of tasks that PyFynance currently can perform:

    :ref:`task_load_transactions` - Loads your financial transactions from OFX/QFX files into PyFynance for analysis


PyFynance API Documentation
===========================
This section contains all of the API documentation and design patterns for all of the internal classes of PyFynance.
This is provided as a service to other engineers who wish to modify/fork PyFynance for their own work.
API documentation was generated using Sphinx-apidoc

|

.. toctree::
   :maxdepth: 4
   
	PyFynance Architecture <architecture.rst>
	
.. toctree::
   :maxdepth: 4
   
	PyFynance Testing Approach <tests/tests.rst>
	
.. toctree::
   :maxdepth: 4
   
	Core Package <apidoc/PyFynance.core.rst>
	
.. toctree::
   :maxdepth: 4
   
	Resources Package <apidoc/PyFynance.resources.rst>
	
.. toctree::
   :maxdepth: 4
   
	Schemas Package <apidoc/PyFynance.schemas.rst>
	
.. toctree::
   :maxdepth: 4
   
	Services Package <apidoc/PyFynance.services.rst>
	
.. toctree::
   :maxdepth: 4
   
	Tasks Package <apidoc/PyFynance.tasks.rst>
