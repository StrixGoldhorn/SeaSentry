# backend/app/modules/alerts/custom_rules.py

from pydantic import BaseModel, TypeAdapter
from typing import List, Union, Literal, Any
from app.models.vessel import VesselLocation
from sqlalchemy.orm import aliased
from sqlalchemy import  select, and_, or_, not_, exists, func
from geoalchemy2 import Geography
from app.models.vessel import VesselData, VesselLocation, VesselOfInterest
from app.models.geofence import Geofence
from datetime import timedelta, datetime

ALLOWED_FIELDS = Literal[
    'shipname',
    'shiptype',
    'mmsi',
    'speed',
    'proximity_to_shiptype',
    'inside_geofence',
    'enter_geofence',
    'exit_geofence',
    'is_vessel_of_interest'
]
ALLOWED_OPERATORS = Literal['=', '!=', '>', '<', '>=', '<=', 'LIKE']
ALLOWED_COMBINATORS = Literal['and', 'or', 'not']

class LeafRule(BaseModel):
    field: ALLOWED_FIELDS
    operator: ALLOWED_OPERATORS
    value: Any
    valueShiptype: str | None = None
    valueGeofenceid: int | None = None

class GroupRule(BaseModel):
    combinator: ALLOWED_COMBINATORS
    rules: List[Union['LeafRule', 'GroupRule']]

GroupRule.model_rebuild()
RuleTree = Union[LeafRule, GroupRule]

RuleTreeAdapter = TypeAdapter(RuleTree)

def get_geofence_poly_subquery(geofence_id: str):
    '''
    Helper function to return query for geofence polygon given a geofence id

    Args:
        id: geofence id
    
    Returns:
        Query for geofence polygon given a geofence id
    '''
    return (
        select(Geofence.geofence_polygon)
        .where(Geofence.geofence_id == geofence_id)
        .scalar_subquery()
    )

def get_prev_coords_subquery():
    PrevLoc = aliased(VesselLocation)
    return (
        select(PrevLoc.vessel_location_coords)
        .where(
            PrevLoc.vessel_location_vessel_data_id == VesselLocation.vessel_location_vessel_data_id,
            PrevLoc.vessel_location_id < VesselLocation.vessel_location_id
        )
        .order_by(PrevLoc.vessel_location_id.desc())
        .limit(1)
        .scalar_subquery()
    )

def get_recent_inside_geofence_subquery(geofence_id: str):
    PastLoc = aliased(VesselLocation)

    poly_subquery = (
        select(Geofence.geofence_polygon)
        .where(Geofence.geofence_id == geofence_id)
        .scalar_subquery()
    )

    return (
        select(1)
        .select_from(PastLoc)
        .where(
            PastLoc.vessel_location_vessel_data_id == VesselLocation.vessel_location_vessel_data_id,
            PastLoc.vessel_location_id < VesselLocation.vessel_location_id,
            PastLoc.vessel_location_timestamp >= datetime.now() - timedelta(hours=1),
            func.ST_Contains(poly_subquery, PastLoc.vessel_location_coords).is_(True)
        )
    )

def build_sqlalchemy_expression(node: Union[LeafRule, GroupRule]):
    '''
    Recursively builds a safe SQLAlchemy WHERE clause expression.
    '''
    if isinstance(node, LeafRule):

        # ship_name
        if node.field == 'shipname':
            if node.operator == 'LIKE': return VesselData.vessel_data_ship_name.ilike(f"%{node.value}%")
            if node.operator == '=': return VesselData.vessel_data_ship_name == str(node.value)
            raise ValueError("Invalid operator for shipname")

        # ship_type
        elif node.field == 'shiptype':
            if node.operator == '=': return VesselData.vessel_data_ship_type == node.value
            if node.operator == '!=': return VesselData.vessel_data_ship_type != node.value
            raise ValueError("Invalid operator for shiptype")

        # mmsi
        elif node.field == 'mmsi':
            if node.operator == '=': return VesselData.vessel_data_mmsi == str(node.value)
            raise ValueError("Only '=' operator is allowed for mmsi")

        # speed
        elif node.field == 'speed':
            if node.operator == '>': return VesselLocation.vessel_location_speed_knots > float(node.value)
            if node.operator == '<': return VesselLocation.vessel_location_speed_knots < float(node.value)
            if node.operator == '>=': return VesselLocation.vessel_location_speed_knots >= float(node.value)
            if node.operator == '<=': return VesselLocation.vessel_location_speed_knots <= float(node.value)
            if node.operator == '=': return VesselLocation.vessel_location_speed_knots == float(node.value)
            raise ValueError("Invalid operator for speed")

        # proximity
        elif node.field == 'proximity_to_shiptype':
            if not node.valueShiptype:
                raise ValueError("proximity_to_shiptype requires valueShiptype")

            v2 = aliased(VesselLocation)
            vd2 = aliased(VesselData)

            subquery = select(1).select_from(v2).join(
                vd2, v2.vessel_location_vessel_data_id == vd2.vessel_data_id
            ).where(
                vd2.vessel_data_ship_type == node.valueShiptype,
                func.ST_DWithin(
                    func.Cast(VesselLocation.vessel_location_coords, Geography),
                    func.Cast(v2.vessel_location_coords, Geography),
                    float(node.value)
                )
            )
            return exists(subquery)

        # inside geofence
        elif node.field == 'inside_geofence':
            if not node.valueGeofenceid:
                raise ValueError("inside_geofence requires valueGeofenceid")

            poly = get_geofence_poly_subquery(node.valueGeofenceid)
            current_inside = func.ST_Contains(poly, VesselLocation.vessel_location_coords).is_(True)

            recent_inside_subquery = get_recent_inside_geofence_subquery(node.valueGeofenceid)

            return and_(current_inside, not_(exists(recent_inside_subquery)))

        # enter geofence
        elif node.field == 'enter_geofence':
            if not node.valueGeofenceid:
                raise ValueError("enter_geofence requires valueGeofenceid")

            poly = get_geofence_poly_subquery(node.valueGeofenceid)
            prev_coords = get_prev_coords_subquery()

            current_inside = func.ST_Contains(poly, VesselLocation.vessel_location_coords)
            prev_inside = func.ST_Contains(poly, prev_coords)

            return and_(current_inside.is_(True), prev_inside.is_not(True))

        # exit geofence
        elif node.field == 'exit_geofence':
            if not node.valueGeofenceid:
                raise ValueError("exit_geofence requires valueGeofenceid")

            poly = get_geofence_poly_subquery(node.valueGeofenceid)
            prev_coords = get_prev_coords_subquery()

            current_inside = func.ST_Contains(poly, VesselLocation.vessel_location_coords)
            prev_inside = func.ST_Contains(poly, prev_coords)

            return and_(current_inside.is_not(True), prev_inside.is_(True))

        # is vessel of interest?
        elif node.field == 'is_vessel_of_interest':
            subquery = select(1).select_from(VesselOfInterest).where(
                or_(
                    VesselOfInterest.vessel_of_interest_mmsi == VesselData.vessel_data_mmsi,
                    VesselOfInterest.vessel_of_interest_imo == VesselData.vessel_data_imo
                )
            )
            return exists(subquery)

    elif isinstance(node, GroupRule):
        # recursively build expressions for all rules in group
        expressions = [build_sqlalchemy_expression(rule) for rule in node.rules]

        if node.combinator == 'and':
            return and_(*expressions)
        elif node.combinator == 'or':
            return or_(*expressions)
        elif node.combinator == 'not':
            return not_(and_(*expressions))

    raise ValueError("Invalid rule structure detected")
