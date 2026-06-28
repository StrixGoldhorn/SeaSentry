from app.core.database import DBConn
from app.utils.aoi_helpers import DBG_INSERT_DEFAULT_AOI
from app.utils.geofence_helpers import DBG_INSERT_DEFAULT_GEOFENCE

def main():
    try:
        DBConn.run_init_sql()
    except:
        print("FAILED TO INTIALISE DATABASE")

    try:
        DBG_INSERT_DEFAULT_AOI()
        DBG_INSERT_DEFAULT_GEOFENCE()
    except:
        print("FAILED TO INSERT DEFAULT AOI/GEOFENCE")


if __name__ == "__main__":
    main()
