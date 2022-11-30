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

import sys
sys.path.insert(0, '/usr/local/lib/python3.11/site-packages')

from osgeo import osr
import mapscript
from mapscript import MapServerError

from pygeoapi.provider.base import (BaseProvider, ProviderConnectionError,
                                    ProviderQueryError)

LOGGER = logging.getLogger(__name__)


IMAGE_FORMATS = {
    'png': 'GD/PNG',
    'png24': 'GD/PNG24',
    'gif': 'GD/GIF',
    'jpeg': 'GD/JPEG'
}


class MapScriptProvider(BaseProvider):
    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition

        :returns: pygeoapi.provider.mapscript_.MapScriptProvider
        """

        BaseProvider.__init__(self, provider_def)

        self.crs_list = []
        self.styles = []
        self._classes = []
        self.default_format = 'png'

        try:
            self._map = mapscript.mapObj()
            self._layer = mapscript.layerObj(self._map)
            self._layer.status = mapscript.MS_ON
            self._layer.data = self.data
            print("PROJECTION", self._layer.getProjection())

            try:
                self.crs = int(self.options['projection'])
            except KeyError:
                self.crs = 4326

            self._layer.setProjection(self._get_proj4_string(self.crs))

            if 'sld' in self.options:
                LOGGER.debug('Setting SLD')
                with open(self.options['sld']) as fh:
                    self._layer.applySLD(fh.read(), self.options['layer_name'])

        except MapServerError as err:
            LOGGER.warning(err)
            raise ProviderConnectionError('Cannot connect to map service')

        self.max_width = self.max_height = self._map.maxsize

    def query(self, style=None, bbox=[], width=500, height=300, crs='CRS84',
              datetime_=None, format_='png'):
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

        try:
            image_obj_format = IMAGE_FORMATS[format_]
        except KeyError:
            LOGGER.error('Bad output format: {}'.format(image_obj_format))
            raise ProviderQueryError('Bad image format')

        LOGGER.debug('Setting coordinate reference system')
        try:
            if crs not in ['CRS84', 4326]:
                LOGGER.debug('Reprojecting')
                prj_dst_text = self._get_proj4_string(int(crs.split("/")[-1]))

                prj_src = mapscript.projectionObj(self._layer.getProjection())
                prj_dst = mapscript.projectionObj(prj_dst_text)

                rect = mapscript.rectObj(*bbox)
                _ = rect.project(prj_src, prj_dst)

                map_bbox = [rect.minx, rect.miny, rect.maxx, rect.maxy]
                map_crs = prj_dst_text

            else:
                map_bbox = bbox
                map_crs = self._get_proj4_string(4326)

        except MapServerError as err:
            LOGGER.error(err)
            raise ProviderQueryError('bad projection')

        LOGGER.debug('Setting output image properties')
        fmt = mapscript.outputFormatObj(image_obj_format)
        fmt.transparent = mapscript.MS_ON

        self._map.setOutputFormat(fmt)
        self._map.setExtent(*map_bbox)
        self._map.setSize(width, height)

        self._map.setProjection(map_crs)
        self._map.setConfigOption('MS_NONSQUARE', 'yes')

        print("BBOX", bbox)
        #self._layer.setExtent(*bbox)
        img = self._map.draw()

        return img.getBytes()

    def _get_proj4_string(self, epsg_code):
        prj = osr.SpatialReference()
        prj.ImportFromEPSG(epsg_code)

        return prj.ExportToProj4().strip()

    def __repr__(self):
        return '<MapScriptProvider> {}'.format(self.data)
