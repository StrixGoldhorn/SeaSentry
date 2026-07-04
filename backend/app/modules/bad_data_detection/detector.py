from sqlalchemy import desc, func, and_
from datetime import timedelta

from app.core.config import Settings
from app.models.vessel import VesselLocation
from app.models.source import RawData
from app.utils.audit_log_helpers import write_audit_log
from app.modules.alerts.deduplication import check_and_record_alert

def detector(session, vessel_data_id: int, vessel_location_id: int):
    '''
    Evaluates a specific vessel location against other scrapers and historical data.
    '''
    current_loc = session.query(VesselLocation).get(vessel_location_id)
    if not current_loc:
        return

    current_source_id = session.query(RawData.raw_data_data_source_id).filter(
        RawData.raw_data_id == current_loc.vessel_location_raw_data_id
    ).scalar()

    # timespan
    time_start = current_loc.vessel_location_timestamp - timedelta(seconds=Settings.TIME_TOLERANCE_SECONDS)
    time_end = current_loc.vessel_location_timestamp + timedelta(seconds=Settings.TIME_TOLERANCE_SECONDS)

    # distance between points
    distance_expr = func.ST_DistanceSphere(
        VesselLocation.vessel_location_coords,
        current_loc.vessel_location_coords
    )

    # discrepancy between sources check
    conflicting_report = session.query(VesselLocation).join(RawData).filter(
        VesselLocation.vessel_location_vessel_data_id == vessel_data_id, # same vessel
        RawData.raw_data_data_source_id != current_source_id, # different source
        VesselLocation.vessel_location_timestamp.between(time_start, time_end), # within timespan
        distance_expr > Settings.SPATIAL_TOLERANCE_METERS # more than tolerance
    ).first()

    if conflicting_report:
        conflict_source_id = session.query(RawData.raw_data_data_source_id).filter(
            RawData.raw_data_id == conflicting_report.vessel_location_raw_data_id
        ).scalar()
        check_and_record_alert(
            session, 2,
            {
                "reason": f"spatial mismatch: >{Settings.SPATIAL_TOLERANCE_METERS}m",
                "source 1": current_source_id,
                "source 2": conflict_source_id,
                "vessel_data_id": conflicting_report.vessel_location_vessel_data_id
            }
        )

    # teleport/speeding check
    if current_loc.vessel_location_speed_knots is not None and current_loc.vessel_location_speed_knots > 0:
        prev_window_start = current_loc.vessel_location_timestamp - timedelta(minutes=Settings.SPEED_CHECK_WINDOW_MINUTES)

        prev_loc = session.query(VesselLocation).join(RawData).filter(
            VesselLocation.vessel_location_vessel_data_id == vessel_data_id, # same vessel
            RawData.raw_data_data_source_id == current_source_id, # same source
            VesselLocation.vessel_location_timestamp < current_loc.vessel_location_timestamp, # timestamp is older
            VesselLocation.vessel_location_timestamp >= prev_window_start # within timeframe
        ).order_by(VesselLocation.vessel_location_timestamp.desc()).first()

        if prev_loc:
            time_diff_seconds = (current_loc.vessel_location_timestamp - prev_loc.vessel_location_timestamp).total_seconds()

            if time_diff_seconds > 0:
                dist_meters_val = session.query(
                    func.ST_DistanceSphere(prev_loc.vessel_location_coords, current_loc.vessel_location_coords)
                ).scalar()

                if dist_meters_val and dist_meters_val > 0:
                    implied_speed_ms = dist_meters_val / time_diff_seconds
                    implied_speed_knots = implied_speed_ms * 1.94384

                    current_speed = current_loc.vessel_location_speed_knots
                    prev_speed = prev_loc.vessel_location_speed_knots

                    if current_speed is not None and prev_speed is not None:
                        max_reported_speed = max(current_speed, prev_speed)

                        if implied_speed_knots > max_reported_speed + Settings.SPEED_BUFFER_KNOTS:
                            check_and_record_alert(
                            session, 2,
                            {
                                "reason": f"Distance covered more than given speed + buffer {Settings.SPEED_BUFFER_KNOTS}",
                                "current speed": current_speed,
                                "prev speed": prev_speed,
                                "location_id 1": current_loc.vessel_location_id,
                                "location_id 2": prev_loc.vessel_location_id
                            }
                        )
                    else:
                        return
