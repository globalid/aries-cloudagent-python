"""Represents a feature discovery disclosure message."""

from typing import Mapping, Sequence

from marshmallow import EXCLUDE, fields, Schema, validate, ValidationError

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import DISCLOSE, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.disclose_handler.DiscloseHandler"


class Disclose(AgentMessage):
    """Represents a feature discovery disclosure, the response to a query message."""

    class Meta:
        """Disclose metadata."""

        handler_class = HANDLER_CLASS
        message_type = DISCLOSE
        schema_class = "DiscloseSchema"

    def __init__(self, *, protocols: Sequence[Mapping[str, Mapping]] = None, **kwargs):
        """
        Initialize disclose message object.

        Args:
            protocols: A mapping of protocol names to a dictionary of properties
        """
        super().__init__(**kwargs)
        self.protocols = list(protocols) if protocols else []


class ProtocolOrGoalCodeDescriptorField(fields.Field):
    """ProtocolDescriptor or GoalCodeDescriptor for Marshmallow."""

    def _serialize(self, value, attr, obj, **kwargs):
        return value

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, (str, dict)):
            return value
        else:
            raise ValidationError(
                "Field should be ProtocolDescriptor or GoalCodeDescriptor"
            )


class ProtocolDescriptorSchema(Schema):
    """Schema for an entry in the protocols list."""

    id = fields.Str(required=True)
    feature_type = fields.Str(
        required=True, description="feature-type", data_key="feature-type"
    )
    roles = fields.List(
        fields.Str(
            description="Role: requester or responder",
            example="requester",
            validate=validate.OneOf(["requester", "responder"]),
        ),
        required=False,
        allow_none=True,
        description="List of roles",
    )


class GoalCodeDescriptorSchema(Schema):
    """Schema for an entry in the goal_code list."""

    id = fields.Str(required=True)
    feature_type = fields.Str(
        required=True, description="feature-type", data_key="feature-type"
    )


class DiscloseSchema(AgentMessageSchema):
    """Disclose message schema used in serialization/deserialization."""

    class Meta:
        """DiscloseSchema metadata."""

        model_class = Disclose
        unknown = EXCLUDE

    protocols = fields.List(
        fields.Nested(ProtocolDescriptorSchema()),
        required=True,
        description="List of protocol descriptors",
    )
