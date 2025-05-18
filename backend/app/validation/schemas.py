from marshmallow import Schema, fields, validate, ValidationError

class NotificationSettingsSchema(Schema):
    email = fields.Bool(required=False, load_default=True)
    sms = fields.Bool(required=False, load_default=False)
    preferredTime = fields.Str(
        required=False,
        load_default="immediate",
        validate=validate.OneOf(["immediate", "daily", "weekly"])
    )

class TrackedItemSchema(Schema):
    itemId = fields.Str(required=True)
    title = fields.Str(required=True)
    currentPrice = fields.Float(required=True)
    targetPrice = fields.Float(required=True)
    currency = fields.Str(required=True, validate=validate.Length(equal=3))
    lastChecked = fields.DateTime(required=False)
    alertSent = fields.Bool(required=False, load_default=False)

class CreateUserSchema(Schema): 
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    notification_settings = fields.Nested(NotificationSettingsSchema, required=False)
    tracked_items = fields.List(fields.Nested(TrackedItemSchema), required=False, load_default=[])