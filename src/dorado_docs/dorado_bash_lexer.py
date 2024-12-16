"""
Extends Pygments BashLexer to add "dorado" and it's subcommands
as keywords for highlighting
"""

from pygments.lexers.shell import BashLexer  # pylint: disable=E0401
from pygments.token import Keyword  # pylint: disable=E0401


class DoradoBashLexer(BashLexer):
    """
    Bash script lexer extension to add syntax highlighting to dorado commands
    """

    name = "DoradoBash"
    aliases = ["dorado"]

    def __init__(self, **options):
        super().__init__(**options)
        dorado_root = Keyword.Constant
        dorado_subcommand = Keyword.Namespace
        dorado_help = Keyword.Reserved
        dorado_operator = Keyword.Type

        self.custom_keywords = {
            "dorado": dorado_root,
            "--help": dorado_help,
            "aligner": dorado_subcommand,
            "basecaller": dorado_subcommand,
            "duplex": dorado_subcommand,
            "demux": dorado_subcommand,
            "correct": dorado_subcommand.Double,
            "download": dorado_subcommand,
            "summary": dorado_subcommand,
            "trim": dorado_subcommand,
            "polish": dorado_subcommand,
            ">": dorado_operator,
            "|": dorado_operator,
        }

    def get_tokens_unprocessed(self, text):
        """Intercepts base class lexer and adds custom settings"""
        for index, token, value in super().get_tokens_unprocessed(text):
            if value in self.custom_keywords:
                yield index, self.custom_keywords[value], value
            else:
                yield index, token, value
