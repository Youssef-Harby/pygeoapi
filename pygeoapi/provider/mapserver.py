# =================================================================
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2020 Tom Kralidis
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
#sys.path.insert(0, '/usr/local/Cellar/mapserver/7.6.1/lib/python3.8/site-packages')

import mapscript
from mapscript import MapServerError

from pygeoapi.provider.base import (BaseProvider, ProviderConnectionError,
                                    ProviderInvalidQueryError,
                                    ProviderQueryError)

LOGGER = logging.getLogger(__name__)


class MapServerMapfileProvider(BaseProvider):
    def __init__(self, provider_def):
        """
        Initialize object

        :param provider_def: provider definition

        :returns: pygeoapi.provider.mapserver_mapfile.MapServerMapfileProvider
        """

        BaseProvider.__init__(self, provider_def)

        self.crs_list = []
        self.styles = []
        self._classes = []
        self.default_format = 'png'

        try:
            self._map = mapscript.mapObj(self.data)
        except MapServerError as err:
            LOGGER.warning(err)
            raise ProviderConnectionError('Cannot connect to map service')

        self.max_width = self.max_height = self._map.maxsize
        self._layer = self._map.getLayerByName(self.options['layer_name'])

        try:
            self.crs_list = self._layer.metadata.get(
                'wms_srs', self._layer.metadata.get('ows_srs')).split()
        except AttributeError as err:
            LOGGER.warning('No CRS list found: {}'.format(err))
            self.crs_list = []

        if 'sld' in self.options:
            LOGGER.debug('Applying custom SLD')
            status = self._layer.applySLD(open(self.options['sld']).read(),
                                          self.options['layer_name'])
            LOGGER.debug('Applying custom SLD status: {}'.format(status))

        for s in range(0, self._layer.numclasses):
            cls = self._layer.getClass(s)
            if cls.group is not None:
                self.styles.append(cls.group)

    def get_legend(self, style, format_='png'):
        """
        Generate a legend from a MapServer layer configuration

        :param style: style name
        :param format_: Output format (default is `png`)

        :returns: bytes of legend image
        """

        if style is not None and style not in self.styles:
            LOGGER.warning('Invalid style name: {}'.format(style))
            raise ProviderInvalidQueryError('Invalid style name')

        width = height = 32

        for s in range(0, self._layer.numclasses):
            cls = self._layer.getClass(s)
            if cls.group is not None and cls.group == style:
                legend_icon = cls.createLegendIcon(
                    self._map, self._layer, width, height)
                return legend_icon.getBytes()

    def query(self, style, bbox=[], width=500, height=300, crs='CRS84',
              format_='png'):
        """
        Generate a map from a MapServer mapfile configuration

        :param bbox: bounding box [minx,miny,maxx,maxy]
        :param width: width of output image (in pixels)
        :param height: height of output image (in pixels)
        :param datetime: temporal (datestamp or extent)
        :param crs: coordinate reference system identifier
        :param format_: Output format (default is `png`)

        :returns: dict of 0..n GeoJSON features
        """

        if style is not None and style not in self.styles:
            LOGGER.warning('Invalid style name: {}'.format(style))
            raise ProviderInvalidQueryError('Invalid style name')

        if format_ == 'png':
            image_obj_format = 'GD/PNG'
        elif format_ == 'gif':
            image_obj_format = 'GD/GIF'
        elif format_ == 'jpeg':
            image_obj_format = 'GD/JPEG'
        elif format_ == 'png24':
            image_obj_format = 'GD/PNG24'
        else:
            LOGGER.warning('Bad output format: {}'.format(image_obj_format))
            raise ProviderQueryError('Bad image format')

        LOGGER.debug('Setting coordinate reference system')
        try:

            print("CRS", crs)
            if crs not in ['CRS84', 4326]:
                prj_src_text = '+init=epsg:4326'
                prj_dst_text = f'+init={crs.lower()}'

                prj_src = mapscript.projectionObj(prj_src_text)
                prj_dst = mapscript.projectionObj(prj_dst_text)

                # status = self._layer.setProjection(prj_dst_text)
                status = self._map.setProjection(prj_dst_text)
                self._map.units = mapscript.MS_METERS

                rect = mapscript.rectObj(*bbox)
                status = rect.project(prj_src, prj_dst)
                bbox = [rect.minx, rect.miny, rect.maxx, rect.maxy]

        except MapServerError as err:
            LOGGER.warning(err)
            raise ProviderQueryError('bad projection')

        LOGGER.debug('Setting output image properties')
        fmt = mapscript.outputFormatObj(image_obj_format)
        fmt.transparent = mapscript.MS_ON
        # img = mapscript.imageObj(width, height, fmt)
        img = self._map.prepareImage()

        print(f'width: {width}')
        print(f'height: {height}')
        print(f'bbox: {bbox}')

        self._map.setOutputFormat(fmt)
        self._map.setExtent(*bbox)
        self._map.setSize(width, height)

        if 'sld' in self.options:
            LOGGER.debug('Applying custom SLD')
            status = self._layer.applySLD(open(self.options['sld']).read(),
                                          self.options['layer_name'])
            LOGGER.debug('Applying custom SLD status: {}'.format(status))

        if style != 'default':
            self._layer.classgroup = style

        LOGGER.debug('Drawing layer {} with style {}'.format(
            self.options['layer_name'], style))
        self._layer.draw(self._map, img)
        # img = self._map.draw()

        return img.getBytes()

        def __repr__(self):
            return '<MapServerMapfileProvider> {}'.format(self.data)
