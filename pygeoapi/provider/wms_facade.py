# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2022 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging
from urllib.parse import urlencode

import pyproj
import requests

print("PYPROJ", pyproj.__version__)
from pygeoapi.provider.base import (BaseProvider, ProviderConnectionError,
                                    ProviderQueryError)

LOGGER = logging.getLogger(__name__)

OUTPUT_FORMATS = {
    'png': 'image/png'
}

CRS_CODES = {
    4326: 'CRS:84',
    'http://www.opengis.net/def/crs/EPSG/0/3857': 'EPSG:3857'
}


class WMSFacadeProvider(BaseProvider):
    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition

        :returns: pygeoapi.provider.map_facade.WMSFacadeProvider
        """

        BaseProvider.__init__(self, provider_def)

        self.max_width = self.max_height = None

    def query(self, style=None, bbox=[-180, -90, 180, 90], width=500,
              height=300, crs=4326, datetime_=None, format_='png'):
        """
        Generate map

        :param style: style name (default is `None`)
        :param bbox: bounding box [minx,miny,maxx,maxy]
        :param width: width of output image (in pixels)
        :param height: height of output image (in pixels)
        :param datetime_: temporal (datestamp or extent)
        :param crs: coordinate reference system identifier
        :param format_: Output format (default is `png`)

        :returns: `bytes` of map image
        """

        if crs in [4326, 'CRS;84']:
            bbox2 = ','.join(str(c) for c in
                             [bbox[1], bbox[0], bbox[3], bbox[2]])
        else:
            src_crs = pyproj.CRS.from_string('epsg:4326')
            dest_crs = pyproj.CRS.from_string(CRS_CODES[crs])

            transformer = pyproj.Transformer.from_crs(src_crs,
                dest_crs, always_xy=True)

            minx, miny = transformer.transform(bbox[0], bbox[1])
            maxx, maxy = transformer.transform(bbox[2], bbox[3])

            bbox2 = ','.join(str(c) for c in [minx, miny, maxx, maxy])

        params = {
            'version': '1.3.0',
            'service': 'WMS',
            'request': 'GetMap',
            'bbox': bbox2,
            'crs': CRS_CODES[crs],
            'layers': self.options['layer'],
            'styles': self.options.get('style', 'default'),
            'width': width,
            'height': height,
            'format': OUTPUT_FORMATS[format_]
        }

        if '?' in self.data:
            request_url = '&'.join([self.data, urlencode(params)])
        else:
            request_url = '?'.join([self.data, urlencode(params)])

        print("REQUEST URL", request_url)

        response = requests.get(request_url)

        if b'ServiceException' in response.content:
            msg = f'WMS error: {response.content}'
            LOGGER.error(msg)
            raise ProviderQueryError(msg)

        return response.content


# GOOD: https://www.mapsforeurope.org/maps/wms?token=ImV1cm9nZW9ncmFwaGljc19yZWdpc3RlcmVkXzM3MjIi.FmeBBQ.O6mrj1ubZRr7DDG8436aaGtXiPY&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&BBOX=1739084.391878958791,4904140.352874076925,2310018.9421312185,5122765.332810065709&SRS=EPSG:3857&WIDTH=1183&HEIGHT=454&LAYERS=egm&STYLES=default&FORMAT=image/png&DPI=72&MAP_RESOLUTION=72&FORMAT_OPTIONS=dpi:72&TRANSPARENT=TRUE
# BAD: https://www.mapsforeurope.org/maps/wms?token=ImV1cm9nZW9ncmFwaGljc19yZWdpc3RlcmVkXzM3MjIi.FmeBBQ.O6mrj1ubZRr7DDG8436aaGtXiPY&version=1.3.0&service=WMS&request=GetMap&bbox=-18785164.07136492%2C-21995848.722816914%2C18785164.07136492%2C21995848.722816937&crs=EPSG%3A3857&layers=egm&styles=default&width=800&height=600&format=image%2Fpng

        with open('/Users/tomkralidis/Desktop/Screenshot 2022-11-30 at 02.39.29.png', 'rb') as fh:
            return fh.read()

    def __repr__(self):
        return '<MapScriptProvider> {}'.format(self.data)
