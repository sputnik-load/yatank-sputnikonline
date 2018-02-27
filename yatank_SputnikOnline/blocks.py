from yandextank.plugins import Codes
from yandextank.plugins.ConsoleOnline import NoConsoleMarkup
from yandextank.plugins.ConsoleScreen import CurrentTimesDistBlock
from yandextank.plugins.ConsoleScreen import CurrentHTTPBlock
from yandextank.plugins.ConsoleScreen import CurrentNetBlock
from yandextank.plugins.ConsoleScreen import CasesBlock
from yandextank.plugins.ConsoleScreen import TotalQuantilesBlock
from yandextank.plugins.ConsoleScreen import AnswSizesBlock
from yandextank.plugins.ConsoleScreen import AvgTimesBlock


class MockScreen(object):

    def __init__(self):
        self.markup = NoConsoleMarkup()


class OnlineTimesDistBlock(CurrentTimesDistBlock):

    def __init__(self):
        CurrentTimesDistBlock.__init__(self, MockScreen())

    def render(self):
        CurrentTimesDistBlock.render(self)
        return self.lines


class OnlineHTTPBlock(CurrentHTTPBlock):

    def __init__(self):
        CurrentHTTPBlock.__init__(self, MockScreen())

    def render(self):
        CurrentHTTPBlock.render(self)
        return self.lines


class OnlineNetBlock(CurrentNetBlock):

    def __init__(self):
        CurrentNetBlock.__init__(self, MockScreen())

    def render(self):
        CurrentNetBlock.render(self)
        return self.lines


class OnlineCasesBlock(CasesBlock):

    def __init__(self):
        CasesBlock.__init__(self, MockScreen())

    def render(self):
        CasesBlock.render(self)
        return self.lines


class OnlineTotalQuantilesBlock(TotalQuantilesBlock):

    def __init__(self):
        TotalQuantilesBlock.__init__(self, MockScreen())

    def render(self):
        TotalQuantilesBlock.render(self)
        return self.lines


class OnlineAnswSizesBlock(AnswSizesBlock):

    def __init__(self):
        AnswSizesBlock.__init__(self, MockScreen())

    def render(self):
        AnswSizesBlock.render(self)
        return self.lines


class OnlineAvgTimesBlock(AvgTimesBlock):

    def __init__(self):
        AvgTimesBlock.__init__(self, MockScreen())

    def render(self):
        AvgTimesBlock.render(self)
        return self.lines
