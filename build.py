from pathlib import Path

from pybuilder.core import use_plugin, init, Author, before


use_plugin('python.core')
use_plugin('python.distutils')
use_plugin('python.flake8')
use_plugin('python.unittest')

use_plugin('pypi:pybuilder_pycharm_workspace')
use_plugin('pypi:pybuilder_archetype_base')

path = Path(__file__).resolve().parent

name = path.name
authors = [Author("CEF Digital", '')]
license = "European Union Public Licence, V. 1.2"
version = '0.1.0'
description = "FIWARE Context Broker Linked Data instance integration with the BDTI"
url = 'https://github.com/ConnectingEurope/Context-Broker-BDTI-LD'

entry_points = {
	'console_scripts': "cb-bdti=cb_bdti.commands:cli"
}


default_task = ['clean', 'publish']

@init
def initialise(project):
	project.depends_on_requirements('requirements.txt')

	project.set_property('dir_source_main_python', 'src')

	project.set_property('dir_source_unittest_python', 'tests')
	project.set_property('unittest_module_glob', 'test_*')

	project.set_property('project_base_path', path)
	project.set_property('pycharm_workspace_project_path', path)

	project.set_property('distutils_entry_points', entry_points)

@init(environments='develop')
def initialise_dev(project):
	project.version = f'{project.version}.dev'
	project.set_property('flake8_verbose_output', True)


@init(environments='production')
def initialise_pro(project):
	project.set_property('flake8_break_build', True)
	project.set_property('flake8_include_test_sources', True)



@before('prepare')
def pack_files(project):
	"""
    Includes non-Python files in the build.
	:param pybuilder.core.Project project: PyBuilder project instance
	:return: None
    """
	package_path = list(Path(project.get_property('dir_source_main_python')).glob('*'))[0]
	resources_paths = sorted(package_path.glob('**'))[1:]
	project.package_data.update(
		{package_path.name: [str((path.relative_to(package_path) / '*').as_posix()) for path in resources_paths]})

if __name__ == '__main__':
	import sys

	if len(sys.argv) > 1 and sys.argv[1] == 'pycharm_builder':
		from subprocess import run

		pyb_command = ['pyb'] + sys.argv[2:]
		run(pyb_command)  # Add more complexity here as desired
	else:
		print("Nothing to do here")
