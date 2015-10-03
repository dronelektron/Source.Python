# ../core/command.py

"""Registers the "sp" server command and all of its sub-commands."""

# =============================================================================
# >> IMPORTS
# =============================================================================
# Site-Package Imports
#   Configobj
from configobj import ConfigObj

# Source.Python Imports
#   Auth
from auth.commands import _auth_commands
#   Autodoc
from autodoc import SphinxProject
#   Core
from core import core_logger
from core import dumps
from core.manager import core_plugin_manager
from core.version import VERSION
#   Cvars
from cvars import ConVar
#   Engines
from engines.server import engine_server
#   Paths
from paths import SP_DOCS_PATH
from paths import CUSTOM_PACKAGES_DOCS_PATH
from paths import PLUGIN_DOCS_PATH
from paths import SP_PACKAGES_PATH
from paths import CUSTOM_PACKAGES_PATH
from paths import PLUGIN_PATH
from paths import SP_DATA_PATH
#   Plugins
from plugins import _plugin_strings
from plugins.command import SubCommandManager
from plugins.info import PluginInfo
from plugins.instance import LoadedPlugin
#   Tick
from listeners.tick import tick_delays


# =============================================================================
# >> GLOBAL VARIABLES
# =============================================================================
# Get the sp.core.command logger
core_command_logger = core_logger.command


# =============================================================================
# >> CLASSES
# =============================================================================
class _CoreLoadedPlugin(LoadedPlugin):

    """Plugin instance class used to create "sp" loaded plugins."""

    logger = core_command_logger


class _CoreCommandManager(SubCommandManager):

    """Class used for executing "sp" sub-command functionality."""

    manager = core_plugin_manager
    instance = _CoreLoadedPlugin
    logger = core_command_logger

    def print_plugins(self):
        """List all currently loaded plugins."""
        # Get header messages
        message = self.prefix + _plugin_strings[
            'Plugins'].get_string() + '\n' + '=' * 61 + '\n\n'

        # Loop through all loaded plugins
        for plugin_name in sorted(self.manager):
            info = self.manager[plugin_name].info

            # Was an PluginInfo instance found?
            if info is not None:

                # Add message with the current plugin's name
                message += plugin_name + ':\n'

                # Loop through all items in the PluginInfo instance
                for item, value in info.items():

                    # Is the value a ConVar?
                    if isinstance(value, ConVar):

                        # Get the ConVar's text
                        value = '{0}:\n\t\t\t{1}: {2}'.format(
                            value.get_name(),
                            value.get_help_text(),
                            value.get_string())

                    # Add message for the current item and its value
                    message += '\t{0}:\n\t\t{1}\n'.format(item, value)

            # Was no PluginInfo instance found?
            else:

                # Add message with the current plugin's name
                message += plugin_name + '\n'

            # Add 1 blank line between each plugin
            message += '\n'

        # Add the ending separator
        message += '=' * 61

        # Print the message
        self.logger.log_message(message)

    @staticmethod
    def delay_execution(*args):
        """Execute a command after the given delay."""
        tick_delays.delay(
            float(args[0]),
            engine_server.server_command, ' '.join(args[1:]) + '\n')

    def dump_data(self, dump_type, filename):
        """Dump data to logs."""
        # Does the given dump type exist as a function?
        if not 'dump_{0}'.format(dump_type) in dumps.__all__:

            # If not, print message to notify of unknown dump type
            self.logger.log_message(
                'Invalid dump_type "{0}". The valid types are:'.format(
                    dump_type))

            # Loop though all dump functions
            for dump in dumps.__all__:

                # Print the current dump function
                self.logger.log_message(
                    '\t{0}'.format(dump.replace('dump_', '')))

            # No need to go further
            return

        # Call the function
        getattr(dumps, 'dump_{0}'.format(dump_type))(filename)

    # Set the methods arguments
    dump_data.args = ['<dump_type>', '<filename>']

    def print_version(self):
        """Display Source.Python version information."""
        self.logger.log_message(
            'Current Source.Python version: {0}'.format(VERSION))

    def docs_handler(self, action, package):
        """Create, generate or build a Sphinx project."""
        if action == 'create':
            self._create_sphinx_project(package)
        elif action == 'generate':
            self._generate_sphinx_project(package)
        elif action == 'build':
            self._build_sphinx_project(package)
        else:
            self.logger.log_message(('Invalid action: "{0}". Valid action are'
                ': create, generate and build'.format(action)))
    docs_handler.args = ['<action>', '<package>']

    def _create_sphinx_project(self, package):
        """Create a Sphinx project."""
        if self.is_source_python(package):
            self._create_source_python_docs()
        elif self.is_custom_package(package):
            self._create_custom_package_docs(package)
        elif self.is_plugin(package):
            self._create_plugin_docs(package)
        else:
            self.logger.log_message(('"{0}" is not source-python, a custom pa'
                'ckage or a plugin.'.format(package)))

    def _generate_sphinx_project(self, package):
        """Generate project files for a Sphinx project."""
        if self.is_source_python(package):
            self._generate_source_python_docs()
        elif self.is_custom_package(package):
            self._generate_custom_package_docs(package)
        elif self.is_plugin(package):
            self._generate_plugin_docs(package)
        else:
            self.logger.log_message(('"{0}" is not source-python, a custom pa'
                'ckage or a plugin.'.format(package)))

    def _build_sphinx_project(self, package):
        """Build project files for a Sphinx project."""
        if self.is_source_python(package):
            self._build_source_python_docs()
        elif self.is_custom_package(package):
            self._build_custom_package_docs(package)
        elif self.is_plugin(package):
            self._build_plugin_docs(package)
        else:
            self.logger.log_message(('"{0}" is not source-python, a custom pa'
                'ckage or a plugin.'.format(package)))

    def _create_source_python_docs(self):
        """Create a Sphinx project for Source.Python."""
        project = SphinxProject(SP_PACKAGES_PATH, SP_DOCS_PATH)
        if project.project_exists():
            self.logger.log_message(
                'Sphinx project already exists for Source.Python')
        else:
            try:
                project.create('Source.Python Development Team',
                    'Source.Python', VERSION)
            except:
                self.logger.log_message(('An occured while creating Sphinx pr'
                    'oject for Source.Python.'))
            else:
                self.logger.log_message(
                    'Sphinx project has been created for Source.Python.')

    def _create_custom_package_docs(self, package):
        """Create a Sphinx project for a custom package."""
        project = SphinxProject(CUSTOM_PACKAGES_PATH / package,
            CUSTOM_PACKAGES_DOCS_PATH / package)
        if project.project_exists():
            self.logger.log_message(('Sphinx project already exists for custo'
                'm package "{0}".'.format(package)))
        else:
            try:
                project.create('Unknown')
            except:
                self.logger.log_message(('An error occured while creating Sph'
                    'inx project for custom package "{0}".'.format(package)))
            else:
                self.logger.log_message(('Sphinx project has been created for'
                    ' custom package "{0}".'.format(package)))

    def _create_plugin_docs(self, package):
        """Create a Sphinx project for a plugin."""
        project = SphinxProject(PLUGIN_PATH / package,
            PLUGIN_DOCS_PATH / package)
        if project.project_exists():
            self.logger.log_message(('Sphinx project already exists for plugi'
                'n "{0}".'.format(package)))
        else:
            try:
                project.create('Unknown')
            except:
                self.logger.log_message(('An error occured while creating Sph'
                    'inx project for plugin "{0}".'.format(package)))
            else:
                self.logger.log_message(('Sphinx project has been created for'
                    ' plugin "{0}".'.format(package)))

    def _generate_source_python_docs(self):
        """Generate Sphinx project files for Source.Python."""
        project = SphinxProject(SP_PACKAGES_PATH, SP_DOCS_PATH)
        if project.project_exists():
            try:
                project.generate_project_files()
            except:
                self.logger.log_message(('An error occured while generating p'
                    'roject files for Source.Python'))
            else:
                # TODO: Make sure we replace the correct source-python
                #       occurences
                # We need to get rid of "source-python." in the module path
                for file_path in project.project_source_dir.files('*.rst'):
                    with file_path.open() as f:
                        data = f.read()

                    with file_path.open('w') as f:
                        f.write(data.replace('source-python.', ''))

                self.logger.log_message(
                    'Project files have been generated for Source.Python.')
        else:
            self.logger.log_message(
                'Sphinx project does not exist for Source.Python.')

    def _generate_custom_package_docs(self, package):
        """Generate Sphinx project files for a custom package."""
        project = SphinxProject(CUSTOM_PACKAGES_PATH / package,
            CUSTOM_PACKAGES_DOCS_PATH / package)
        if project.project_exists():
            try:
                project.generate_project_files()
            except:
                self.logger.log_message(('An error occured while generating p'
                    'roject files for custom package "{0}".'.format(package)))
            else:
                self.logger.log_message(('Project files have been generated f'
                    'or custom package "{0}".'.format(package)))
        else:
            self.logger.log_message(('Sphinx project does not exist for custo'
                'm package "{0}".'.format(package)))

    def _generate_plugin_docs(self, package):
        """Generate Sphinx project files for a plugin."""
        project = SphinxProject(PLUGIN_PATH / package,
            PLUGIN_DOCS_PATH / package)
        if project.project_exists():
            try:
                project.generate_project_files()
            except:
                self.logger.log_message(('An error occured while generating p'
                    'roject files for plugin "{0}".'.format(package)))
            else:
                self.logger.log_message(('Project files have been generated f'
                    'or plugin "{0}".'.format(package)))
        else:
            self.logger.log_message(('Sphinx project does not exist for plugi'
                'n "{0}".'.format(package)))

    def _build_source_python_docs(self):
        """Build Sphinx project files for Source.Python."""
        project = SphinxProject(SP_PACKAGES_PATH, SP_DOCS_PATH)
        if project.project_exists():
            # Update version and release
            conf_file = project.project_source_dir / 'conf.py'
            with conf_file.open() as f:
                lines = f.readlines()

            with conf_file.open('w') as f:
                for line in lines:
                    if line.startswith(('version', 'release')):
                        line = '{0} = \' {1}\'\n'.format(
                            line.split(maxsplit=1)[0], VERSION)

                    f.write(line)

            try:
                project.build()
            except:
                self.logger.log_message(('An error occured while building pro'
                    'ject files for Source.Python.'))
            else:
                self.logger.log_message(
                    'Project files have been built for Source.Python.')
        else:
            self.logger.log_message(
                'Sphinx project does not exist for Source.Python.')

    def _build_custom_package_docs(self, package):
        """Build Sphinx project files for a custom package."""
        project = SphinxProject(CUSTOM_PACKAGES_PATH / package,
            CUSTOM_PACKAGES_DOCS_PATH / package)
        if project.project_exists():
            try:
                project.build()
            except:
                self.logger.log_message(('An error occured while building pro'
                    'ject files for custom package "{0}".'.format(package)))
            else:
                self.logger.log_message(('Project files have been built for c'
                    'ustom package "{0}".'.format(package)))
        else:
            self.logger.log_message(('Sphinx project does not exist for custo'
                'm package "{0}".'.format(package)))

    def _build_plugin_docs(self, package):
        """Build Sphinx project files for a plugin."""
        project = SphinxProject(PLUGIN_PATH / package,
            PLUGIN_DOCS_PATH / package)
        if project.project_exists():
            try:
                project.build()
            except:
                self.logger.log_message(('An error occured while building pro'
                    'ject files for plugin "{0}".'.format(package)))
            else:
                self.logger.log_message(('Project files have been built for p'
                    'lugin "{0}".'.format(package)))
        else:
            self.logger.log_message(('Sphinx project does not exist for plugi'
                'n "{0}".'.format(package)))

    @staticmethod
    def is_source_python(package):
        """Return True if the given package name is source-python."""
        return package == 'source-python'

    @staticmethod
    def is_custom_package(package):
        """Return True if the given package name is a custom package."""
        return package in map(
            lambda path: str(path.namebase), CUSTOM_PACKAGES_PATH.listdir())

    @staticmethod
    def is_plugin(package):
        """Return True if the given package name is a plugin."""
        return package in map(
            lambda path: str(path.namebase), PLUGIN_PATH.dirs())

    def print_credits(self):
        """List all credits for Source.Python."""
        # Get header messages
        message = self.prefix + _plugin_strings[
            'Credits'].get_string() + '\n' + '=' * 61 + '\n\n'

        # Get the credits information
        groups = ConfigObj(
            SP_DATA_PATH.joinpath('credits.ini'), encoding='unicode_escape')

        # Loop through all groups in the credits
        for group in groups:

            # Add the current group's name
            message += '\t' + group + ':\n'

            # Loop through all names in the current group
            for name in groups[group]:

                # Add the current name
                message += '\t\t' + name + ' ' * (
                    20 - len(name)) + groups[group][name] + '\n'

            # Add 1 blank line between groups
            message += '\n'

        # Print the message
        self.logger.log_message(message + '=' * 61 + '\n\n')

# Get the _CoreCommandManager instance
_core_command = _CoreCommandManager('sp', 'Source.Python base command.')

# Register the load/unload sub-commands
_core_command['load'] = _core_command.load_plugin
_core_command['unload'] = _core_command.unload_plugin
_core_command['reload'] = _core_command.reload_plugin

# Register the 'auth' sub-command
_core_command['auth'] = _auth_commands

# Register the 'delay' sub-command
_core_command['delay'] = _core_command.delay_execution
_core_command['delay'].args = ['<delay>', '<command>', '[arguments]']

# Register the 'dump' sub-command
_core_command['dump'] = _core_command.dump_data

# Register all printing sub-commands
_core_command['list'] = _core_command.print_plugins
_core_command['version'] = _core_command.print_version
_core_command['credits'] = _core_command.print_credits
_core_command['help'] = _core_command.print_help

# Register the 'docs' sub-command
_core_command['docs'] = _core_command.docs_handler
