from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component


class FleetService(Component):
    _inherit = "base.rest.service"
    _name = "fleet.service"
    _usage = "fleet"
    _collection = "base.rest.fleet.public.services"
    _description = """
        Fleet Services
        Services developed with the new api provided by base_rest
    """

    @restapi.method(
        [(["/<int:id>/get", "/<int:id>"], "GET")],
        output_param=Datamodel("fleet.vehicle.info"),
        auth="public",
    )
    def get(self, _id):
        """
        Get fleet's information
        """
        fleet = self._get(_id)
        FleetInfo = self.env.datamodels["fleet.vehicle.info"]
        fleet_info = FleetInfo(partial=True)
        fleet_info.id = fleet.id
        fleet_info.name = fleet.name
        fleet_info.driver = self.env.datamodels["fleet.driver"](
            id=fleet.driver_id.id,
            name=fleet.driver_id.name
        )
        fleet_info.license_plate = fleet.license_plate
        fleet_info.vehicle_type = self.env.datamodels["fleet.vehicle.type"](
            name=fleet.vehicle_type,
            brand=self.env.datamodels["fleet.vehicle.brand"](
                id=fleet.brand_id.id,
                name=fleet.brand_id.name
            )
        )
        return fleet_info

    @restapi.method(
        [(["/search"], "GET")],
        input_param=Datamodel("fleet.vehicle.search.param"),
        output_param=Datamodel("fleet.vehicle.basic.info", is_list=True),
        auth="public",
    )
    def search(self, fleet_search_param):
        """
        Search for fleet
        :param fleet_search_param: An instance of fleet.vehicle.search.param
        :return: List of fleet.vehicle.basic.info
        """
        domain = []
        if fleet_search_param.id:
            domain.append(("id", "=", fleet_search_param.id))
        if fleet_search_param.name:
            domain.append(("name", "like", fleet_search_param.name))
        if fleet_search_param.driver:
            domain.append(("driver_id", "like", fleet_search_param.driver))
        if fleet_search_param.vehicle_type:
            domain.append(
                ("vehicle_type", "=", fleet_search_param.vehicle_type))
        if fleet_search_param.license_plate:
            domain.append(
                ("license_plate", "=", fleet_search_param.license_plate))
        res = []
        FleetBasicInfo = self.env.datamodels["fleet.vehicle.basic.info"]
        for fleet in self.env["fleet.vehicle"].search(domain):
            res.append(FleetBasicInfo(
                id=fleet.id,
                name=fleet.name,
                vehicle_type=self.env.datamodels["fleet.vehicle.type"](
                    name=fleet.vehicle_type,
                    brand=self.env.datamodels["fleet.vehicle.brand"](
                        id=fleet.brand_id.id,
                        name=fleet.brand_id.name
                    )
                ),
                driver=self.env.datamodels["fleet.driver"](
                    id=fleet.driver_id.id,
                    name=fleet.driver_id.name
                )
            ))
        return res

    # The following method are 'private' and should be never never NEVER call
    # from the controller.

    def _get(self, _id):
        return self.env["fleet.vehicle"].browse(_id)
