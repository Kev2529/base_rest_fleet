from marshmallow import fields

from odoo.addons.datamodel.core import Datamodel
from odoo.addons.datamodel.fields import NestedModel


class FleetVehicleBasicInfo(Datamodel):
    _name = "fleet.vehicle.basic.info"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)
    vehicle_type = NestedModel("fleet.vehicle.type")
    driver = NestedModel("fleet.driver")

class FleetVehicleInfo(Datamodel):
    _name = "fleet.vehicle.info"
    _inherit = "fleet.vehicle.basic.info"

    active = fields.Boolean(required=False, allow_none=True)
    license_plate = fields.String(required=True, allow_none=False)


class FleetVehicleType(Datamodel):
    _name = "fleet.vehicle.type"

    name = fields.String(required=True, allow_none=False)
    brand = NestedModel("fleet.vehicle.brand")


class FleetVehicleBrand(Datamodel):
    _name = "fleet.vehicle.brand"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)


class FleetDriver(Datamodel):
    _name = "fleet.driver"

    id = fields.Integer(required=True, allow_none=False)
    name = fields.String(required=True, allow_none=False)


class FleetSearchParam(Datamodel):
    _name = "fleet.vehicle.search.param"

    id = fields.Integer(required=False, allow_none=True)
    name = fields.String(required=False, allow_none=True)
    vehicle_type = fields.String(required=False, allow_none=True, load_default="car")
    license_plate = fields.String(required=False, allow_none=True)
    driver = fields.String(required=False, allow_none=True)
