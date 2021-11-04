from odoo import _
from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_datamodel.restapi import Datamodel
from odoo.addons.component.core import Component
from odoo.http import request
from odoo.exceptions import (
    AccessDenied,
    AccessError,
    MissingError,
    UserError,
    ValidationError,
)
import time
import jwt
import base64


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
        output_param=Datamodel("fleet.vehicle.info", partial=True),
        auth="public",
    )
    def get_vehicle(self, _id):
        """
        Get vehicle's information
        """
        vehicle = self._get_car(_id)
        VehicleInfo = self.env.datamodels["fleet.vehicle.info"]
        vehicle_info = VehicleInfo(partial=True)
        vehicle_info.id = vehicle.id
        vehicle_info.name = vehicle.name
        if (vehicle.driver_id):
            vehicle_info.driver = self.env.datamodels["fleet.driver"](
                id=vehicle.driver_id.id,
                name=vehicle.driver_id.name
            )
        vehicle_info.license_plate = vehicle.license_plate
        return vehicle_info

    @restapi.method(
        [(["/get_attachment_list/<int:id>"], "GET")],
        auth="public",
    )
    def get_pdf_attachment_list(self, _id):
        """
        Get list of pdf's attachment of given vehicle's id
        """
        # Check if vehicle type's car otherwise raise error
        self._get_car(_id)

        res = []
        attachments_ids = self.env['ir.attachment'].search([
            ('res_model', '=', 'fleet.vehicle'),
            ('res_id', '=', _id),
            ('mimetype', '=', 'application/pdf')
        ])
        ids = [_id['id'] for _id in attachments_ids]
        return ids

    @restapi.method(
        [(["/get_attachment/<int:id>"], "GET")],
        auth="public",
    )
    def get_attachment(self, _id):
        """
        Get file attachment of pdf type vehicle car only
        """
        attachment_id = self.env['ir.attachment'].search([
            ('res_model', '=', 'fleet.vehicle'),
            ('id', '=', _id),
            ('mimetype', '=', 'application/pdf')
        ])
        # Check if vehicle type's car otherwise raise error
        if attachment_id:
            self._get_car(attachment_id.res_id)
        else:
            raise ValidationError(_("Attachment not allowed"))
        # Get status, headers & content from webserver to make response later
        status, headers, content = self.env["ir.http"].binary_content(
            model="ir.attachment",
            id=attachment_id.id,
            download=True # uncomment to allow download format
        )
        content = base64.b64decode(content) # uncomment to change into b64
        if content:
            headers.append(("Content-Length", len(content)))
        res = request.make_response(content, headers)
        res.status_code = status
        return res

    @restapi.method(
        [(["/search"], "GET")],
        input_param=Datamodel("fleet.vehicle.search.param"),
        output_param=Datamodel("fleet.vehicle.basic.info", is_list=True),
        auth="public",
    )
    def search_car(self, fleet_search_param):
        """
        Search for vehicle of type car only
        :param fleet_search_param: An instance of fleet.vehicle.search.param
        :return: List of fleet.vehicle.basic.info
        """
        domain = [("vehicle_type", "=", 'car')]
        if fleet_search_param.id:
            domain.append(("id", "=", fleet_search_param.id))
        if fleet_search_param.name:
            domain.append(("name", "like", fleet_search_param.name))
        if fleet_search_param.driver:
            domain.append(("driver_id", "ilike", fleet_search_param.driver))
        if fleet_search_param.license_plate:
            domain.append(
                ("license_plate", "=", fleet_search_param.license_plate))
        res = []
        FleetBasicInfo = self.env.datamodels["fleet.vehicle.basic.info"]
        for vehicle in self.env["fleet.vehicle"].search(domain):
            res.append(FleetBasicInfo(
                id=vehicle.id,
                name=vehicle.name,
                driver=self.env.datamodels["fleet.driver"](
                    id=vehicle.driver_id.id,
                    name=vehicle.driver_id.name
                )
            ))
        return res

    # The following method are 'private' and should be never never NEVER call
    # from the controller.

    def _get_car(self, _id):
        vehicle = self.env["fleet.vehicle"].browse(_id)
        # Check if vehicle type's car otherwise raise error
        self._check_car_type(vehicle)
        return self.env["fleet.vehicle"].browse(_id)

    def _check_car_type(self, vehicles):
        for vehicle in vehicles:
            if vehicle.vehicle_type != 'car':
                # Choose wanted error message
                # 404 Missing
                raise MissingError(_("Missing Ressource Test"))
                # 403 Access Denied
                # raise AccessDenied()
