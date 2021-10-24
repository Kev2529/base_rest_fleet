from odoo.addons.base_rest.controllers import main


class BaseRestFleetApiController(main.RestController):
    _root_path = "/base_rest_fleet_api/new_api/"
    _collection_name = "base.rest.fleet.public.services"
    _default_auth = "public"
