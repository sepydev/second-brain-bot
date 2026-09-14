import importlib
import pkgutil

from telegram.ext import Application, CommandHandler

from second_brain_bot.bot.command import Command


def discover_commands() -> list[Command]:
    import second_brain_bot.bot.commands as commands_package

    commands = []

    for module_info in pkgutil.iter_modules(commands_package.__path__):
        module = importlib.import_module(
            f"{commands_package.__name__}.{module_info.name}"
        )

        for value in vars(module).values():
            if (
                isinstance(value, type)
                and issubclass(value, Command)
                and value is not Command
            ):
                commands.append(value())

    return commands


def register_commands(application: Application) -> list[Command]:
    commands = discover_commands()

    for command in commands:
        application.add_handler(
            CommandHandler(
                command.name,
                command.execute,
            )
        )

    return commands