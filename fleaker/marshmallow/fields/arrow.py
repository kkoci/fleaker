# ~*~ coding: utf-8 ~*~
"""Module that defines a Marshmallow field that deserialzes a date string into
an Arrow object.
"""

from __future__ import absolute_import

from datetime import datetime

import arrow

from marshmallow import ValidationError, fields

from fleaker._compat import text_type

from .mixin import FleakerFieldMixin


class ArrowField(fields.DateTime, FleakerFieldMixin):
    """Marshmallow field that deserialzes datetimes into Arrow objects.

    Has the same output on dump as the standard DateTime field. Accepts the
    same kwargs on init.

    This field is effected by the following schema context variables:

    - ``'convert_dates'``: This will prevent the date string from being
        converted into an Arrow object. This can be useful if you're going to
        be double deserialzing the value in the course of the request. This is
        needed for Webargs. By default, dates will be converted.

    Keyword Args:
        timezone (str): The timezone that the datetime must be in. If it
            doesn't match, a ``marshmallow.ValidationError`` is raised.
    """

    def _jsonschema_type_mapping(self):
        """Define the JSON Schema type for this field."""
        result = {
            'type': 'string',
            'format': 'date-time',
        }

        # @TODO This is needed because marshmallow jsonschema doesn't support
        # setting these attributes like it does with built-ins. Fix this
        # upstream and remove this code.
        if self.metadata.get('metadata', {}).get('description'):
            result['description'] = self.metadata['metadata']['description']

        if self.metadata.get('metadata', {}).get('title'):
            result['title'] = self.metadata['metadata']['title']

        return result

    def _serialize(self, value, attr, obj):
        """Convert the Arrow object into a string."""
        if isinstance(value, arrow.arrow.Arrow):
            value = value.datetime

        return super(ArrowField, self)._serialize(value, attr, obj)

    def _deserialize(self, value, attr, data):
        """Deserializes a string into an Arrow object."""
        if not self.context.get('convert_dates', True):
            return value

        value = super(ArrowField, self)._deserialize(value, attr, data)
        timezone = self.get_field_value('timezone')

        if isinstance(value, datetime):
            target = arrow.get(value)

            if (timezone and
                    text_type(target.to(timezone)) != text_type(target)):
                raise ValidationError(
                    "The provided datetime is not in the "
                    "{} timezone.".format(timezone)
                )

            return target

        return value
