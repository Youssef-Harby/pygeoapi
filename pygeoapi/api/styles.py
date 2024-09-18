# =================================================================

# Authors: Joana Simoes <jo@doublebyte.net>
#
# Copyright (c) 2024 Joana Simoes
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
import os
from http import HTTPStatus
from typing import Tuple, List

from pygeoapi.util import to_json, render_j2_template
from . import APIRequest, API, F_JSON, F_HTML, SYSTEM_LOCALE, FORMAT_TYPES

LOGGER = logging.getLogger(__name__)

CONFORMANCE_CLASSES = [
    'http://www.opengis.net/spec/ogcapi-styles-1/0.0/conf/core',
    'http://www.opengis.net/spec/ogcapi-styles-1/0.0/conf/html',
    'http://www.opengis.net/spec/ogcapi-styles-1/0.0/conf/mapbox-style'
]


def get_styles(api: API, request: APIRequest) -> Tuple[dict, int, str]:
    """
    Fetches the set of styles available.
    For each style it returns the id, a title, links to the stylesheet of the style # noqa 
    in each supported encoding, and the link to the metadata.

    :param api: API instance
    :param request: APIRequest object

    :returns: tuple of headers, status code, content
    """
    format_ = request.format or F_JSON

    # Force response content type and language (en-US only) headers
    headers = request.get_response_headers(SYSTEM_LOCALE, **api.api_headers)

    styles = _retrieve_all_styles(api)

    data = {"styles": styles}

    if format_ == F_JSON:
        headers["Content-Type"] = FORMAT_TYPES[F_JSON]
        return headers, HTTPStatus.OK, to_json(data, api.pretty_print)
    elif format_ == F_HTML:
        content = render_j2_template(
            api.tpl_config, "styles/index.html", data, request.locale
        )
        headers["Content-Type"] = FORMAT_TYPES[F_HTML]
        return headers, HTTPStatus.OK, content
    else:
        return api.get_format_exception(request)


def get_style(
        api: API, request: APIRequest, style_id: str) -> Tuple[dict, int, str]:
    """
    Fetches a style by ID.

    :param api: API instance
    :param request: APIRequest object
    :param style_id: Identifier of the style

    :returns: tuple of headers, status code, content
    """
    format_ = request.params.get("f")
    headers = request.get_response_headers(SYSTEM_LOCALE, **api.api_headers)

    style = _retrieve_style(api, style_id)

    if not style:
        return _style_not_found(headers, api, request, style_id)

    # Determine the requested style format
    if format_ == "mapbox":
        media_type = "application/vnd.mapbox.style+json"
        content = _load_style_content(style)
    elif format_ == "sld10":
        media_type = "application/vnd.ogc.sld+xml;version=1.0"
        content = _load_style_content(style)
    elif format_ == "sld11":
        media_type = "application/vnd.ogc.sld+xml;version=1.1"
        content = _load_style_content(style)
    else:
        # Default to mapbox style if no format is specified
        media_type = "application/vnd.mapbox.style+json"
        content = _load_style_content(style)

    if not content:
        return _style_content_not_found(headers, api, request, style_id)

    headers["Content-Type"] = media_type
    return headers, HTTPStatus.OK, content


def get_style_metadata(
    api: API, request: APIRequest, style_id: str
) -> Tuple[dict, int, str]:
    """
    Fetches the metadata about a style.

    :param api: API instance
    :param request: APIRequest object
    :param style_id: Identifier of the style

    :returns: tuple of headers, status code, content
    """
    format_ = request.format or F_JSON
    headers = request.get_response_headers(SYSTEM_LOCALE, **api.api_headers)

    style_metadata = _retrieve_style_metadata(api, style_id)

    if not style_metadata:
        return _style_not_found(headers, api, request, style_id)

    if format_ == F_JSON:
        headers["Content-Type"] = FORMAT_TYPES[F_JSON]
        return headers, HTTPStatus.OK, to_json(
            style_metadata, api.pretty_print)
    elif format_ == F_HTML:
        content = render_j2_template(
            api.tpl_config,
            "styles/style_metadata.html",
            style_metadata,
            request.locale
        )
        headers["Content-Type"] = FORMAT_TYPES[F_HTML]
        return headers, HTTPStatus.OK, content
    else:
        return api.get_format_exception(request)


def get_oas_30(cfg: dict, locale: str) -> tuple[list[dict[str, str]], dict[str, dict]]:  # noqa
    """
    Get OpenAPI fragments

    :param cfg: `dict` of configuration
    :param locale: `str` of locale

    :returns: `tuple` of `list` of tag objects, and `dict` of path objects
    """

    from pygeoapi.openapi import OPENAPI_YAML

    paths = {}

    paths['/styles'] = {
        'get': {
            'summary': 'lists the available styles',
            'description': 'This operation fetches the set of styles available.', # noqa
            'tags': ['Discover and fetch styles'],
            'operationId': 'getStyles',
            'externalDocs': {
                'description': 'The specification that describes this operation: OGC API - Styles (DRAFT)', # noqa
                'url': 'https://docs.ogc.org/DRAFTS/20-009.html'
                },
            'parameters': [
                {'$ref': '#/components/parameters/access_token'},
                {'$ref': '#/components/parameters/fStyles'}
            ],
            'responses': {
                '200': {'$ref': f"{OPENAPI_YAML['oapif-1']}#/components/responses/Features"},  # noqa
                '400': {'$ref': f"{OPENAPI_YAML['oapif-1']}#/components/responses/InvalidParameter"},  # noqa
                # TODO: add 406
                '500': {'$ref': f"{OPENAPI_YAML['oapif-1']}#/components/responses/ServerError"}  # noqa
            }
        }
    }

    return [{'name': 'styles'}], {'paths': paths}
# Helper Functions


def _retrieve_all_styles(api: API) -> List[dict]:
    """
    Retrieve all available styles from the configuration.

    :param api: API instance

    :returns: List of style metadata dictionaries
    """
    styles = []
    resources = api.config.get("resources", {})

    # Loop through collections and their providers to find styles
    for collection_id, collection in resources.items():
        providers = collection.get("providers", [])
        for provider in providers:
            provider_styles = provider.get("styles", [])
            for style in provider_styles:
                style_metadata = _format_style_entry(api, collection_id, style)
                styles.append(style_metadata)

    return styles


def _retrieve_style(api: API, style_id: str) -> dict:
    """
    Retrieve a specific style by its ID.

    :param api: API instance
    :param style_id: Identifier of the style

    :returns: Style dictionary or None
    """
    resources = api.config.get("resources", {})
    for collection_id, collection in resources.items():
        providers = collection.get("providers", [])
        for provider in providers:
            provider_styles = provider.get("styles", [])
            for style in provider_styles:
                if style.get("name") == style_id:
                    return style
    return None


def _retrieve_style_metadata(api: API, style_id: str) -> dict:
    """
    Retrieve the metadata of a specific style.

    :param api: API instance
    :param style_id: Identifier of the style

    :returns: Style metadata dictionary or None
    """
    style = _retrieve_style(api, style_id)
    if not style:
        return None

    # Build the style metadata according to the schema
    metadata = {
        "id": style.get("name"),
        "title": style.get("title"),
        "description": style.get("description"),
        "keywords": style.get("keywords", []),
        "stylesheets": [
            {
                "title": style.get("title"),
                "version": "8",  # Assuming Mapbox GL Style Spec version 8
                "specification": (
                    "https://docs.mapbox.com/mapbox-gl-js/style-spec/"
                    ),
                "native": True,
                "link": {
                    "href": (
                        f"{api.config['server']['url']}/styles/"
                        f"{style.get('name')}?f=mapbox"
                    ),
                    "rel": "stylesheet",
                    "type": "application/vnd.mapbox.style+json",
                },
            }
        ],
        # Add other metadata fields as needed
    }
    return metadata


def _format_style_entry(api: API, collection_id: str, style: dict) -> dict:
    """
    Format a style entry for the /styles response.

    :param api: API instance
    :param collection_id: Identifier of the collection
    :param style: Style dictionary

    :returns: Formatted style entry dictionary
    """
    style_id = style.get("name")
    base_url = api.config["server"]["url"]

    style_entry = {"id": style_id, "links": []}

    # Add links to the style in different formats
    supported_formats = ["mapbox", "sld10", "sld11"]
    for fmt in supported_formats:
        href = f"{base_url}/styles/{style_id}?f={fmt}"
        media_type = _get_media_type_for_format(fmt)
        style_entry["links"].append(
            {
                "href": href,
                "rel": "stylesheet",
                "type": media_type,
                "title": f"Style in {fmt.upper()} format",
            }
        )

    # Link to style metadata
    style_entry["links"].append(
        {
            "href": f"{base_url}/styles/{style_id}/metadata",
            "rel": "metadata",
            "type": "application/json",
            "title": "Style metadata",
        }
    )

    return style_entry


def _load_style_content(style: dict) -> str:
    """
    Load the content of a style from its data path.

    :param style: Style dictionary

    :returns: Style content as a string or None
    """
    style_data = style.get("style", {}).get("data")
    if style_data and os.path.exists(style_data):
        with open(style_data, "r") as f:
            return f.read()
    return None


def _style_not_found(headers, api, request, style_id):
    """
    Handle style not found error.

    :param headers: Response headers
    :param api: API instance
    :param request: APIRequest object
    :param style_id: Style identifier

    :returns: tuple of headers, status code, content
    """
    msg = f"Style {style_id} not found"
    return api.get_exception(
        HTTPStatus.NOT_FOUND, headers, request.format, "NotFound", msg
    )


def _style_content_not_found(headers, api, request, style_id):
    """
    Handle style content not found error.

    :param headers: Response headers
    :param api: API instance
    :param request: APIRequest object
    :param style_id: Style identifier

    :returns: tuple of headers, status code, content
    """
    msg = f"Style content for {style_id} not found"
    return api.get_exception(
        HTTPStatus.NOT_FOUND, headers, request.format, "NotFound", msg
    )


def _get_media_type_for_format(format_: str) -> str:
    """
    Get the media type for a given style format.

    :param format_: Format string ('mapbox', 'sld10', 'sld11')

    :returns: Media type string
    """
    if format_ == "mapbox":
        return "application/vnd.mapbox.style+json"
    elif format_ == "sld10":
        return "application/vnd.ogc.sld+xml;version=1.0"
    elif format_ == "sld11":
        return "application/vnd.ogc.sld+xml;version=1.1"
    else:
        return "application/json"  # Default
