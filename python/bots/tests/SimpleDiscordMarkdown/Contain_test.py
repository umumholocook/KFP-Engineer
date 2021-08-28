import inspect

from common.SimpleDiscordMarkdown import Parser, Rules

def test():
    _rules = {r for _, r
              in inspect.getmembers(Rules, lambda o: isinstance(o, Rules._Rule))}
    assert _rules == {Rules.root, *Parser._rules}
