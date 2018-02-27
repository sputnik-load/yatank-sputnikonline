''' local webserver with online graphs '''
from threading import Thread

from yandextank.plugins.Monitoring import MonitoringPlugin
from yandextank.plugins.Aggregator import \
    AggregatorPlugin, AggregateResultListener
from yandextank.core import AbstractPlugin
from yandextank.plugins.ConsoleOnline import ConsoleOnlinePlugin

from server import ReportServer
from decode import decode_aggregate, decode_monitoring

from cache import DataCacher
from blocks import OnlineTimesDistBlock, OnlineHTTPBlock
from blocks import OnlineNetBlock, OnlineCasesBlock
from blocks import OnlineTotalQuantilesBlock, OnlineAnswSizesBlock
from blocks import OnlineAvgTimesBlock

import pkg_resources
import logging

class SputnikOnlinePlugin(AbstractPlugin, Thread, AggregateResultListener):

    '''Interactive report plugin '''
    SECTION = "sputnikonline"
    PLUGIN_INFO = {
        "version": pkg_resources.get_distribution("yatank-sputnikonline").version
    }
    DEFAULT_LEVEL_VALUE = 'info'

    @staticmethod
    def get_key():
        return __file__

    def __init__(self, core):
        AbstractPlugin.__init__(self, core)
        Thread.__init__(self)
        self.daemon = True  # Thread auto-shutdown
        self.port = 8080
        self.address = "127.0.0.1"
        self.last_sec = None
        self.server = None
        self.console = None
        self.cache = DataCacher()
        self.render_blocks = {
            "times_dist": OnlineTimesDistBlock(),
            "http": OnlineHTTPBlock(),
            "net": OnlineNetBlock(),
            "cases": OnlineCasesBlock(),
            "quantiles": OnlineTotalQuantilesBlock(),
            "answsizes": OnlineAnswSizesBlock(),
            "avgtimes": OnlineAvgTimesBlock()
        }
        self.log_dir_path = None
        self.log_level = None
        self.log.info("yatank_SputnikOnline %s init ..." \
                      % self.PLUGIN_INFO["version"])

    def get_available_options(self):
        return ['addr', 'port', 'log_dir_path', 'log_level']

    def configure(self):
        self.address = self.get_option("addr", self.address)
        self.port = int(self.get_option("port", self.port))
        level = self.get_option('log_level',
                                SputnikOnlinePlugin.DEFAULT_LEVEL_VALUE)
        levels = {'notset': logging.NOTSET,
                  'debug': logging.DEBUG,
                  'info': logging.INFO,
                  'warning': logging.WARNING,
                  'error': logging.ERROR,
                  'critical': logging.CRITICAL}
        if not levels.get(level):
            self.log.warning("log_level option is not correct, "
                             "will be set '%s'" \
                             % SputnikOnlinePlugin.DEFAULT_LEVEL_VALUE)
            level = SputnikOnlinePlugin.DEFAULT_LEVEL_VALUE
        self.log_level = levels[level]
        self.log_dir_path = self.get_option('log_dir_path', '')

        try:
            aggregator = self.core.get_plugin_of_type(AggregatorPlugin)
            aggregator.add_result_listener(self)
        except KeyError:
            self.log.warning(
                "No aggregator module, no valid report will be available")

        try:
            mon = self.core.get_plugin_of_type(MonitoringPlugin)
            if mon.monitoring:
                mon.monitoring.add_listener(self)
        except KeyError:
            self.log.warning(
                "No monitoring module, monitroing report disabled")

        try:
            self.console = self.core.get_plugin_of_type(ConsoleOnlinePlugin)
        except Exception, ex:
            self.log.warning("Console not found: %s", ex)
            self.console = None

    def prepare_test(self):
        try:
            self.server = ReportServer(self.cache, self.address, self.port,
                                       self.log_dir_path, self.log_level)
            self.server.owner = self
        except Exception, ex:
            self.log.warning("Failed to start web results server: %s", ex)

    def start_test(self):
        self.start()

    def end_test(self, retcode):
        self.log.info("Ended test. Sending command to reload pages.")
        # self.server.reload()
        return retcode

    def run(self):
        if (self.server):
            self.server.serve()
            self.log.info("Server started.")

    def aggregate_second(self, data):
        for key in self.render_blocks:
            self.render_blocks[key].add_second(data)
        (data, dt) = decode_aggregate(data)

        blocks = {}
        for key in self.render_blocks:
            blocks[key] = self.render_blocks[key].render()
        data[dt]["blocks"] = blocks

        if self.console:
            widget_output = []
            for index, widget in sorted(self.console.screen.info_widgets.iteritems(), key=lambda (k, v): (v.get_index(), k)):
                self.log.debug("Rendering info widget #%s: %s", index, widget)
                widget_out = widget.render(self.console.screen).strip()
                if widget_out:
                    widget_output += widget_out.split("\n")
                    widget_output += [""]
            data[dt]["widgets"] = widget_output
        data[dt]["plugin"] = self.PLUGIN_INFO

        self.cache.store(data)
        if self.server is not None:
            message = {
                'data': data,
            }
            self.server.send(message)

    def monitoring_data(self, data):
        data = decode_monitoring(data)[0]
        self.cache.store(data)
        if self.server is not None and len(data):
            message = {
                'data': data,
            }
            self.server.send(message)

    def post_process(self, retcode):
        self.log.info("Building HTML report...")
        report_html = self.core.mkstemp(".html", "report_")
        self.core.add_artifact_file(report_html)
        with open(report_html, 'w') as report_html_file:
            report_html_file.write(
                self.server.render_offline()
            )
        #raw_input('Press Enter to stop report server.')
        self.server.stop()
        del self.server
        self.server = None
        return retcode
