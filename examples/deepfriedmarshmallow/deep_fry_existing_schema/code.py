# Sometimes you can't change a schema's base class -- it might come from
# a third-party library, or a project-wide custom base. Deep-Fried
# Marshmallow gives you three ways to opt in without touching the
# original definition.

from marshmallow import Schema, fields
from deepfriedmarshmallow import (
    deep_fry_schema,
    deep_fry_schema_object,
    JitSchemaMixin,
)


heading("1. A custom base class via JitSchemaMixin")
note(
    "Mix `JitSchemaMixin` into your existing base class. The mixin "
    "adds the JIT machinery while preserving whatever behavior your "
    "base class already provides."
)


class CompanyBaseSchema(Schema):
    """Pretend this lives in a shared internal package."""

    class Meta:
        ordered = True


class UserSchema(JitSchemaMixin, CompanyBaseSchema):
    username = fields.Str()
    email = fields.Email()
    is_admin = fields.Bool()


user = UserSchema().dump(
    {"username": "ada", "email": "ada@example.com", "is_admin": True}
)
display(user, append=True)


heading("2. Patching a schema class with deep_fry_schema()")
note(
    "If you only get a class reference, call `deep_fry_schema(cls)`. "
    "Every instance you create afterwards is JIT-enabled."
)


class OrderSchema(Schema):
    order_id = fields.Int()
    customer = fields.Str()
    total = fields.Float()


deep_fry_schema(OrderSchema)

order_schema = OrderSchema()
display(
    order_schema.dump(
        {"order_id": 42, "customer": "Grace Hopper", "total": 199.95}
    ),
    append=True,
)


heading("3. Patching a single instance with deep_fry_schema_object()")
note(
    "Got a schema instance handed to you by someone else? "
    "`deep_fry_schema_object(instance)` upgrades just that one object "
    "in place."
)


class TicketSchema(Schema):
    ticket_id = fields.Int()
    subject = fields.Str()
    priority = fields.Str()


third_party_instance = TicketSchema()
deep_fry_schema_object(third_party_instance)

display(
    third_party_instance.dump(
        {"ticket_id": 7, "subject": "Coffee machine offline", "priority": "high"}
    ),
    append=True,
)

note(
    "All three approaches share the same rule of thumb: hold on to "
    "the patched class or instance and reuse it, so the generated "
    "serializer stays cached between calls."
)
