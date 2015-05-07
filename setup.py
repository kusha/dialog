from setuptools import setup

setup(name='dialog',
      version='0.3',
      description='Dialog system framework',
      url='http://github.com/kusha/dialog',
      author='Mark Birger',
      author_email='xbirge00@stud.fit.vutbr.cz',
      license='MIT',
      entry_points = {
        'console_scripts': ['dialog_system=dialog.interpreter:run_master'],
	  },
      packages=['dialog'])