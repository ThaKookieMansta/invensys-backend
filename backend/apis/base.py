"""
This module handles the base endpoint routers for the backend
"""
from fastapi import APIRouter
from apis.v1 import route_user, route_login, route_assign_role, \
    route_laptop_details, route_accessories, route_laptop_allocation, \
    route_repair_history, route_laptop_procurement, route_general, \
    route_departments, route_business_units, route_organization_details

api_router = APIRouter()

api_router.include_router(route_user.router, prefix="", tags=["User"])
api_router.include_router(route_login.router, prefix="", tags=["Login"])
# api_router.include_router(route_assign_role.router, prefix="", tags=["roles"])
api_router.include_router(route_laptop_details.router, prefix="",
                          tags=["Laptop details"])
api_router.include_router(route_accessories.router, prefix="",
                          tags=["Accessories"])
api_router.include_router(route_laptop_allocation.router, prefix="",
                          tags=["Allocations"])
api_router.include_router(route_repair_history.router, prefix="",
                          tags=["Repair History"])
api_router.include_router(route_laptop_procurement.router, prefix="",
                          tags=["Procurement"])
api_router.include_router(route_general.router, prefix="", tags=["General"])
api_router.include_router(route_departments.router, prefix="",
                          tags=["Department"])
api_router.include_router(route_business_units.router, prefix="",
                          tags=["Business Units"])
api_router.include_router(route_organization_details.router, prefix="",
                          tags=["Organization Details"])
