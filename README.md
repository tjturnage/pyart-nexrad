# pyart

documentation below from - http://arm-doe.github.io/pyart-docs-travis/setting_up_an_environment.html

Acquiring Anaconda
=======================================

Creating environments using Anaconda is recommended so you can create more than one environment and
keep dependencies separated so there's less risk of conflicts.

To download and install Anaconda https://www.anaconda.com/download/
MiniConda is fine too. Make sure you're using Python 3.6+

While Anaconda is downloading, it will ask if you want to set a path to it, or
let Anaconda set a default path. After choosing, Anaconda should finish
downloading. After it is done, exit the terminal and open a new one to make
sure the environment path is set. If conda command is not found, there is help
on running conda and fixing the environment path, found here:

* `How to Run Conda https://stackoverflow.com/questions/18675907/how-to-run-conda

Creating an Environment in Anaconda
-----------------------------------

Next you'll need to create a conda environment for using Py-ART and its associated packages. 
In my opinion, the easiest way to do this is with an environment file:

* https://github.com/tjturnage/pyart/blob/master/environment.yml

This will additionally install Spyder (my preferred editor), as well as the s3fs package needed
to download radar data from Amazon/AWS.

To create the environment, go to the directory containing the file and use the command:

        conda env create -f environment.yml

This will then create an environment called pyart_env that can be activated by:

        source activate pyart_env

or deactivated after use:

        source deactivate pyart_env

Collaborating with Others
-------------------------

Here there would be information about contributing to this project!
