import click
from cb_bdti.core.main import BDTI
from cb_bdti.utils.helpers import Helpers
from cb_bdti.config.manager import ConfigManager

class SpecialHelpOrder(click.Group):
	def __init__(self, *args, **kwargs):
		self.help_priorities = {}
		super(SpecialHelpOrder, self).__init__(*args, **kwargs)

	def get_help(self, ctx):
		self.list_commands = self.list_commands_for_help
		return super(SpecialHelpOrder, self).get_help(ctx)

	def list_commands_for_help(self, ctx):
		"""reorder the list of commands when listing the help"""
		commands = super(SpecialHelpOrder, self).list_commands(ctx)
		return (c[1] for c in sorted(
			(self.help_priorities.get(command, 1), command)
			for command in commands))

	def command(self, *args, **kwargs):
		"""Behaves the same as `click.Group.command()` except capture
		a priority for listing command names in help.
		"""
		help_priority = kwargs.pop('help_priority', 1)
		help_priorities = self.help_priorities

		def decorator(f):
			cmd = super(SpecialHelpOrder, self).command(*args, **kwargs)(f)
			help_priorities[cmd.name] = help_priority
			return cmd

		return decorator


class MultiOption(click.Option):
	def __init__(self, *args, **kwargs):
		self.save_other_options = kwargs.pop('save_other_options', True)
		nargs = kwargs.pop('nargs', -1)
		assert nargs == -1, 'nargs, if set, must be -1 not {}'.format(nargs)
		super(MultiOption, self).__init__(*args, **kwargs)
		self._previous_parser_process = None
		self._eat_all_parser = None

	def add_to_parser(self, parser, ctx):

		def parser_process(value, state):
			# method to hook to the parser.process
			done = False
			value = [value]
			if self.save_other_options:
				# grab everything up to the next option
				while state.rargs and not done:
					for prefix in self._eat_all_parser.prefixes:
						if state.rargs[0].startswith(prefix):
							done = True
					if not done:
						value.append(state.rargs.pop(0))
			else:
				# grab everything remaining
				value += state.rargs
				state.rargs[:] = []
			value = tuple(value)

			# call the actual process
			self._previous_parser_process(value, state)

		retval = super(MultiOption, self).add_to_parser(parser, ctx)
		for name in self.opts:
			our_parser = parser._long_opt.get(name) or parser._short_opt.get(name)
			if our_parser:
				self._eat_all_parser = our_parser
				self._previous_parser_process = our_parser.process
				our_parser.process = parser_process
				break
		return retval


@click.group(cls=SpecialHelpOrder)
@click.option('--config', '-c', type=click.Path(), default='-', help='The configuration file path.  [optional]')
@click.pass_context
def cli(ctx, config):
	"""
	This application integrates the context data of the CEF Context Broker (CB) with the
	Big Data Test Infrastructure (BDTI). It manages the subscriptions of data models to the Context Broker
	and the connection between the CB and the Cygnus component. The application makes the subscriptions to the CB
	taking the parameters specified in the configuration file. Then Cygnus will receive the notifications
	about the changes of the context data and it will be able to send them to the BDTI according to the rules
	indicated in the configuration file.

	This integration is compatible with NGSI LD specification.

	The commands manage the subscriptions of the data models and the deployment of Cygnus.
	They can also create and show the configuration file.
	
	Use cb-bdti COMMAND --help for more details about each command.
	"""
	ctx.obj = {'config': config}


@cli.command(name="integrate", help_priority=1)
@click.option('--datamodels', '-d', type=click.STRING, nargs=-1, required=True,
			  help='Name of the Data Models to integrate separated by blanks. '
				   'Use "all" to integrate every Data Model.', cls=MultiOption)
@click.pass_context
def integrate(ctx, datamodels):
	""" Integrate Data Models.
	
		Integrates all the Data Models specified in the configuration file given as parameter,
		making a subscription for each one and deploying Cygnus.
	"""
	config = Helpers.get_config_path(ctx.obj['config'])
	bdti_integration = BDTI(config)
	bdti_integration.integrate(datamodels)


@cli.command(name="modify", help_priority=2)
@click.option('--datamodels', '-d', type=click.STRING, required=True,
			  help='Name of the Data Models to modify separated by blanks. '
				   'Use "all" to modify every Data Model.', cls=MultiOption)
@click.option('--force', '-f', is_flag=True, help='This will force the removal of subscriptions.')
@click.pass_context
def modify(ctx, datamodels, force):
	""" Modify Data Models integration.
	
		Modifies the integrations of Data Models given as parameter, making a new subscription for each one and redeploying Cygnus.
		The Data Models to be modified must have been previosuly integrated by using integrate command.
	"""
	config = Helpers.get_config_path(ctx.obj['config'])
	bdti_integration = BDTI(config)
	bdti_integration.modify(datamodels, force)


@cli.command(name="delete", help_priority=3)
@click.option('--datamodels', '-d', type=click.STRING, required=True,
			  help='Name of the Data Models to delete separated by blanks. '
				   'Use "all" to delete every Data Model.', cls=MultiOption)
@click.option('--deploy', '-u', is_flag=True, help='This will redeploy Cygnus.')
@click.option('--force', '-f', is_flag=True, help='This will force the removal of subscriptions.')
@click.pass_context
def delete(ctx, datamodels, deploy, force):
	""" Delete Data Models integration.
	
		Deletes the integration of Data Models given as parameter.
		The data model to be deleted must have been previously integrated by using integrate command.
		Use the parameter --deploy to redeploy Cygnus.
	"""
	config = Helpers.get_config_path(ctx.obj['config'])
	bdti_integration = BDTI(config, delete=True, deploy=deploy)
	bdti_integration.delete(datamodels, deploy, force)


@cli.command(name="show_integrated", help_priority=4)
@click.pass_context
def show_integrated(ctx):
	""" View Data Models already integrated.
	
		These Data Models have been already integrated previously
		and they have an active subscription to Orion.
	"""
	datamodels_info = ConfigManager.get_datamodels_info()
	if not datamodels_info:
		click.echo('\nThere are no integrated Data Models\n')
	else:
		click.echo('\nThese are the Data Models currently integrated: \n')
		for datamodel in datamodels_info:
			for datamodel_name, datamodel_info in datamodel.items():
				click.echo(datamodel_name)
				for key_name, key_value in datamodel_info.items():
					click.echo("\t %s: %s" %(key_name, key_value))
			click.echo("")

@cli.command(name="new_config", help_priority=5)
@click.pass_context
def new_config(ctx):
	""" Generates the configuration file.
	
		It generates an empty configuration file from a template into default path (/etc/cb_bdti.ini).
		If the configuration file already exits a error is given.
	"""
	BDTI.get_config_file()

@cli.command(name="reset", help_priority=7)
@click.option('--force', '-f', is_flag=True, required=False,
			  help='Force the removal of all integrated Data Models.')
@click.pass_context
def reset(ctx, force):
	""" Reset CB-BDTI configuration.
	
		It removes the configuration file and removes all previously integrated datamodels.
	"""
	BDTI.reset(force)


if __name__ == "__main__":
	cli(obj={})
