import csv
import optparse
import os
import textwrap
import sys

from .. import DuplicateReceipt
from .. import NoSuchReceipt
from .. import NoSuchReport
from .. import delete_receipt
from .. import download_receipt
from .. import initialize_gcloud
from .. import list_receipts
from .. import upload_receipt


class InvalidCommandLine(ValueError):
    pass


class NotACommand(object):
    def __init__(self, bogus):
        self.bogus = bogus

    def __call__(self):
        raise InvalidCommandLine('Not a command: %s' % self.bogus)


def _get_csv(args):
    try:
        csv_file, = args
    except:
        raise InvalidCommandLine('Specify one CSV file')
    csv_file = os.path.abspath(os.path.normpath(csv_file))
    if not os.path.exists(csv_file):
        raise InvalidCommandLine('Invalid CSV file: %s' % csv_file)
    with open(csv_file) as f:
        return csv_file, list(csv.DictReader(f))


class UploadReceipt(object):
    """Upload a receipt for a given expense report.
    """
    def __init__(self, receipter, *args):
        self.receipter = receipter
        args = list(args)
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] EMPLOYEE_ID REPORT_ID FILENAME")

        _, args = parser.parse_args(args)
        try:
            self.employee_id, self.report_id, filename = args
        except:
            raise InvalidCommandLine(
                'Specify employee ID, report ID, filename')

        filename = os.path.abspath(
                    os.path.normpath(filename))

        if not os.path.isfile(filename):
            raise InvalidCommandLine(
                'Invalid filename: %s' % filename)

        self.filename = filename

    def __call__(self):
        try:
            upload_receipt(self.employee_id, self.report_id, self.filename)
        except NoSuchReport:
            self.receipter.blather("No such report: %s/%s"
                % (self.employee_id, self.report_id))
        except DuplicateReceipt:
            self.receipter.blather("Duplicate receipt: %s/%s/%s"
                % (self.employee_id, self.report_id, self.filename))
        else:
            self.receipter.blather("Employee-ID: %s" % self.employee_id)
            self.receipter.blather("Report-ID: %s" % self.report_id)
            self.receipter.blather("")
            self.receipter.blather("Uploaded: %s" % self.filename)


class ListReceipts(object):
    """List expense receipts according to specified criteria.
    """
    def __init__(self, receipter, *args):
        self.receipter = receipter
        args = list(args)
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] EMPLOYEE_ID REPORT_ID")

        _, args = parser.parse_args(args)
        try:
            self.employee_id, self.report_id = args
        except:
            raise InvalidCommandLine('Specify employee ID, report ID')

    def __call__(self):
        try:
            filenames = list_receipts(self.employee_id, self.report_id)
        except NoSuchReport:
            self.receipter.blather("No such report: %s/%s"
                                   % (self.employee_id, self.report_id))
        else:
            self.receipter.blather("Employee-ID: %s" % self.employee_id)
            self.receipter.blather("Report-ID: %s" % self.report_id)
            self.receipter.blather("")
            count = 0
            for filename in filenames:
                self.receipter.blather("Receipt: %s" % filename)
                count += 1
            self.receipter.blather("--------------------------")
            self.receipter.blather("Number of receipts: %d" % count)



class DownloadReceipt(object):
    """Downloa a given expense receipt.
    """
    def __init__(self, receipter, *args):
        self.receipter = receipter
        args = list(args)
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] EMPLOYEE_ID REPORT_ID FILENAME")

        options, args = parser.parse_args(args)
        try:
            self.employee_id, self.report_id, self.filename = args
        except:
            raise InvalidCommandLine('Specify employee ID, report ID, filename')

    def __call__(self):
        try:
            download_receipt(self.employee_id, self.report_id, self.filename)
        except NoSuchReport:
            self.receipter.blather("No such report: %s/%s"
                                   % (self.employee_id, self.report_id))
        except NoSuchReceipt:
            self.receipter.blather("No such report: %s/%s"
                                   % (self.employee_id, self.report_id))
        else:
            self.receipter.blather("Employee-ID: %s" % self.employee_id)
            self.receipter.blather("Report-ID: %s" % self.report_id)
            self.receipter.blather("")
            self.receipter.blather("Downloaded: %s" % self.filename)


class DeleteReceipt(object):
    """Delete a receipt for a given expense report.
    """
    def __init__(self, receipter, *args):
        self.receipter = receipter
        args = list(args)
        parser = optparse.OptionParser(
            usage="%prog [OPTIONS] EMPLOYEE_ID REPORT_ID FILENAME")

        _, args = parser.parse_args(args)
        try:
            self.employee_id, self.report_id, filename = args
        except:
            raise InvalidCommandLine(
                'Specify employee ID, report ID, filename')

        self.filename = filename

    def __call__(self):
        try:
            delete_receipt(self.employee_id, self.report_id, self.filename)
        except NoSuchReport:
            self.receipter.blather("No such report: %s/%s"
                % (self.employee_id, self.report_id))
        except NoSuchReceipt:
            self.receipter.blather("No such receipt: %s/%s/%s"
                % (self.employee_id, self.report_id, self.filename))
        else:
            self.receipter.blather("Employee-ID: %s" % self.employee_id)
            self.receipter.blather("Report-ID: %s" % self.report_id)
            self.receipter.blather("")
            self.receipter.blather("Deleted: %s" % self.filename)


_COMMANDS = {
    'upload': UploadReceipt,
    'list': ListReceipts,
    'download': DownloadReceipt,
    'delete': DeleteReceipt,
}


def get_description(command):
    klass = _COMMANDS[command]
    doc = getattr(klass, '__doc__', '')
    if doc is None:
        return ''
    return ' '.join([x.lstrip() for x in doc.split('\n')])


class ExpenseReceipts(object):
    """ Driver for the :command:`review_expenses` command-line script.
    """
    def __init__(self, argv=None, logger=None):
        self.commands = []
        if logger is None:
            logger = self._print
        self.logger = logger
        self.parse_arguments(argv)

    def parse_arguments(self, argv=None):
        """ Parse subcommands and their options from an argv list.
        """
        # Global options (not bound to sub-command)
        mine = []
        queue = [(None, mine)]

        def _recordCommand(arg):
            if arg is not None:
                queue.append((arg, []))

        for arg in argv:
            if arg in _COMMANDS:
                _recordCommand(arg)
            else:
                queue[-1][1].append(arg)

        _recordCommand(None)

        usage = ("%prog [GLOBAL_OPTIONS] "
                 "[command [COMMAND_OPTIONS]* [COMMAND_ARGS]]")
        parser = optparse.OptionParser(usage=usage)

        parser.add_option(
            '-s', '--help-commands',
            action='store_true',
            dest='help_commands',
            help="Show command help")

        parser.add_option(
            '-q', '--quiet',
            action='store_const', const=0,
            dest='verbose',
            help="Run quietly")

        parser.add_option(
            '-v', '--verbose',
            action='count',
            dest='verbose',
            default=1,
            help="Increase verbosity")

        options, args = parser.parse_args(mine)

        self.options = options

        for arg in args:
            self.commands.append(NotACommand(arg))
            options.help_commands = True

        if options.help_commands:
            keys = sorted(_COMMANDS.keys())
            self.error('Valid commands are:')
            for x in keys:
                self.error(' %s' % x)
                doc = get_description(x)
                if doc:
                    self.error(textwrap.fill(doc,
                                             initial_indent='    ',
                                             subsequent_indent='    '))
            return

        for command_name, args in queue:
            if command_name is not None:
                command = _COMMANDS[command_name](self, *args)
                self.commands.append(command)

    def __call__(self):
        """ Invoke sub-commands parsed by :meth:`parse_arguments`.
        """
        if not self.commands:
            raise InvalidCommandLine('No commands specified')

        for command in self.commands:
            command()

    def _print(self, text):  # pragma NO COVERAGE
        sys.stdout.write('%s\n' % text)

    def error(self, text):
        self.logger(text)

    def blather(self, text, min_level=1):
        if self.options.verbose >= min_level:
            self.logger(text)


def main(argv=sys.argv[1:]):
    initialize_gcloud()
    try:
        ExpenseReceipts(argv)()
    except InvalidCommandLine as e:  # pragma NO COVERAGE
        sys.stdout.write('%s\n' % (str(e)))
        sys.exit(1)
