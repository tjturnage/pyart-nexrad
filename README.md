# pyart

documentation below from - http://arm-doe.github.io/pyart-docs-travis/setting_up_an_environment.html

Setting up an Environment
=========================


Anaconda
--------

Creating environments using Anaconda is recommended due to the ability to
create more than one environment. It is also recommended because you can
keep dependencies separate from one another that might conflict if you had
them all in your root environment.

To download and install Anaconda https://www.anaconda.com/download/

While Anaconda is downloading, it will ask if you want to set a path to it, or
let Anaconda set a default path. After choosing, Anaconda should finish
downloading. After it is done, exit the terminal and open a new one to make
sure the environment path is set. If conda command is not found, there is help
on running conda and fixing the environment path, found here:

* `How to Run Conda https://stackoverflow.com/questions/18675907/how-to-run-conda

Setting a Channel
-----------------

Anaconda has a cloud that stores many of its packages. It is recommended, at
times, to use the conda-forge channel instead. Conda-Forge is a community led
collection of packages, and typically contains the most recent versions of the
packages required for Py-ART. Also Py-ART is on Conda-Forge. Having packages in
an environment, within the same channel, helps avoid conflict issues. To add
conda-forge as the priority channel, simply do::

        conda config --add channels conda-forge

You can also just flag the channel when conda install packages such as::

        conda install -c conda-forge numpy

More on managing channels can be found here:

* `Managing Channels <https://conda.io/docs/user-guide/tasks/manage-channels.html>`_

Creating an Environment
-----------------------

There are a few ways to create a conda environment for using Py-ART or other
packages. One way is to use the environment file, found here:

* https://github.com/ARM-DOE/pyart/blob/master/environment.yml

To create an environment using this file, use the command::

        conda env create -f environment.yml

This will then create an environment called pyart_env that can be activated
by::

        source activate pyart_env

or deactivated after use::

        source deactivate pyart_env

Once the environment is created and activated, you can install more packages
into the environment by simply conda installing them. An example of this is,
if you want Jupyter Notebook to run in that enviroment with those packages::

        conda install -c conda-forge jupyter notebook

while that environment is activated. 

 To then run your coding editor within the
environment, run in the command line::

        python

or::

        ipython

or::

        jupyter notebook

or even::

        spyder

depending on what you installed in your environment and want to use for coding.

