"""
Class to showing keyboard-interactive mode.
"""
from typing import Optional
import blessed
from .option import Option
from .types import AnyCallable


class KeyMode:
    def __init__(
            self,
            options: list[Option],
            description: str,
            term: blessed.Terminal = blessed.Terminal()
    ):
        """
        Class to showing keyboard-interactive mode.

        :param options: Options to be shown on screen
        :param description: Description of the screen to be shown on screen
        :param term: Terminal to be interacted with
        """
        self.__options = options
        self.__description = description
        self.__term = term
        
    @property
    def options(self) -> list[Option]:
        """Options to be shown on screen"""
        return self.__options.copy()
    
    @property
    def description(self) -> str:
        """Description of the screen to be shown on screen"""
        return self.__description
    
    def __call__(self):
        """Shows keyboard interaction mode for the given options"""
        
        term = self.__term
        options = self.options
        
        exit_option = Option(
            name='Exit',
            description='Return to the term',
            handler=term.clear()
        )

        options.append(exit_option)

        current_option = 0
        padded_name_len = max([len(option.name) for option in options]) + 2

        use_description = True
        padded_description_lengths = []
        for option in options:
            description = option.get('description', [])
            padded_description_lengths.append(len(option.get('description', [])))
            if not description:
                use_description = False
                break

        padded_description_len = None
        if use_description:
            padded_description_len = max(padded_description_lengths) + 2

        with term.fullscreen(), term.cbreak(), term.hidden_cursor():
            while True:
                print(term.move_yx(0, 0) + term.clear())

                if self.description:
                    print(term.bold_green(self.description + '\n'))

                for i, option in enumerate(options):
                    name = option.name.ljust(padded_name_len)

                    if use_description:
                        description = option.description.ljust(padded_description_len)
                        option_text = f'{name} | {description}'
                    else:
                        option_text = name

                    if i == current_option:
                        print(term.green_reverse(f"> {option_text}"))
                    else:
                        print(f"  {option_text}")

                key = term.inkey()

                last_option_idx = len(options) - 1
                if key.name == 'KEY_UP':
                    if current_option > 0:
                        current_option -= 1
                    else:
                        current_option = last_option_idx
                elif key.name == 'KEY_DOWN':
                    if current_option < last_option_idx:
                        current_option += 1
                    else:
                        current_option = 0
                elif (key.name in ('KEY_BACKSPACE', 'KEY_DELETE') and
                      (deleting_handler := options[current_option].get('deleting_handler'))):
                    deleting_handler()
                    options.pop(current_option)

                    if len(options) > 1:
                        if current_option > 0:
                            current_option -= 1
                        else:
                            current_option += 1
                    else:
                        return
                elif key == '\n' or key.name == 'KEY_ENTER':
                    selected_option = options[current_option]
                    break

        return selected_option.handler()

    @staticmethod
    def screen_option(
            label: str,
            description: Optional[str],
            options: list[Option],
            deleting_handler: Optional[AnyCallable] = None
    ) -> Option:
        """
        Returns an option navigating to a new screen.

        :param label: The label for the option.
        :param description: The description for the option.
        :param options: List of options for the new screen.
        :param deleting_handler: Optional handler for deleting the option.
        :return: The created Option instance.
        """

        def _handler():
            keymode = KeyMode(options, description)
            keymode()

        option = Option(
            name=label,
            handler=_handler,
            deleting_handler=deleting_handler
        )

        return option
