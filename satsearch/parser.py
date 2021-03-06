import argparse
import satsearch.config as config


class SatUtilsParser(argparse.ArgumentParser):

    def __init__(self, search=True, save=True, download=True, output=True, **kwargs):
        """ Initialize a SatUtilsParser """
        dhf = argparse.ArgumentDefaultsHelpFormatter
        super(SatUtilsParser, self).__init__(formatter_class=dhf, **kwargs)
        if search:
            self.add_search_args()
        if save:
            self.add_save_args()
        if download:
            self.add_download_args()
        if output:
            self.add_output_args()
        h = '0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical'
        self.add_argument('-v', '--verbosity', help=h, default=2, type=int)

    def parse_args(self, *args, **kwargs):
        """ Parse arguments """
        args = super(SatUtilsParser, self).parse_args(*args, **kwargs)
        args = vars(args)
        args = {k: v for k, v in args.items() if v is not None}
        if 'date' in args:
            dt = args.pop('date').split(',')
            if len(dt) > 2:
                raise ValueError('Provide date range as single date or comma separated begin/end dates')
            if len(dt) == 1:
                dt = (dt[0], dt[0])
            args['date_from'] = dt[0]
            args['date_to'] = dt[1]

        if 'clouds' in args:
            cov = args.pop('clouds').split(',')
            if len(cov) != 2:
                raise ValueError('Provide cloud coverage range as two comma separated numbers (e.g., 0,20)')
            args['cloud_from'] = int(cov[0])
            args['cloud_to'] = int(cov[1])

        # set global configuration options
        if 'url' in args:
            config.API_URL = args.pop('url')
        if 'datadir' in args:
            config.DATADIR = args.pop('datadir')
        if 'subdirs' in args:
            config.SUBDIRS = args.pop('subdirs')
        if 'filename' in args:
            config.FILENAME = args.pop('filename')

        return args

    def add_search_args(self):
        """ Adds search arguments to a parser """
        group = self.add_argument_group('search parameters')
        group.add_argument('--satellite_name', help='Name of satellite')
        group.add_argument('--scene_id', help='One or more scene IDs', nargs='*', default=None)
        group.add_argument('--intersects', help='GeoJSON Feature (file or string)')
        group.add_argument('--contains', help='lon,lat points')
        group.add_argument('--date', help='Single date or begin and end date (e.g., 2017-01-01,2017-02-15')
        group.add_argument('--clouds', help='Range of acceptable cloud cover (e.g., 0,20)')
        group.add_argument('--param', nargs='*', help='Additional parameters of form KEY=VALUE', action=self.KeyValuePair)
        group.add_argument('--url', help='URL of the API', default=config.API_URL)

    def add_save_args(self):
        group = self.add_argument_group('saving/loading parameters')
        group.add_argument('--load', help='Load search results from file (ignores other search parameters)')
        group.add_argument('--save', help='Save scenes metadata as GeoJSON', default=None)
        group.add_argument('--append', default=False, action='store_true',
                           help='Append scenes to GeoJSON file (specified by save)')

    def add_download_args(self):
        group = self.add_argument_group('download parameters')
        group.add_argument('--datadir', help='Local directory to save images', default=config.DATADIR)
        group.add_argument('--subdirs', default=config.SUBDIRS,
                           help='Save in subdirs based on these metadata keys')
        group.add_argument('--filename', default=config.FILENAME,
                           help='Save files with this filename pattern based on metadata keys')
        group.add_argument('--download', help='Download files', default=None, nargs='*')

    def add_output_args(self):
        """ Add arguments for printing output """
        group = self.add_argument_group('search output')
        group.add_argument('--printsearch', help='Print search parameters', default=False, action='store_true')
        group.add_argument('--printmd', help='Print specified metadata for matched scenes', default=None, nargs='*')
        group.add_argument('--printcal', help='Print calendar showing dates', default=False, action='store_true')
        group.add_argument('--review', help='Interactive review of thumbnails', default=False, action='store_true')

    class KeyValuePair(argparse.Action):
        """ Custom action for getting arbitrary key values from argparse """
        def __call__(self, parser, namespace, values, option_string=None):
            for val in values:
                n, v = val.split('=')
                setattr(namespace, n, v)
