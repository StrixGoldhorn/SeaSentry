# Project SeaSentry

## Motivation 

Maritime traffic data is currently spread out across multiple sites, each with differing coverage, with limited options for free tiers (eg unable to view historical data for vessels , paywall for specific vessel details, etc.). SeaSentry acts as a data aggregator, scraping and combining data from multiple different sources to get a unified view, combining the data gained from various different sources into a locally hosted API. This allows users to freely track and record historical data of vessels without having to pay. Exposing our own API will allow users to better make use of the data in different ways, be it via plugins or integrating it into their own applications.


## Aim 

We hope to build a locally hosted server that provides an API endpoint and a UI where users can query for data such as current location, historical tracks, etc of different vessels.

Additional features such as geofencing, alerts, specific vessel tracking may follow later.

In the backend, the application will be scraping data from different sites and formatting and inserting the details into a database that the user controls.

We aim to provide a plugin based system for data sources, to allow users to add their own data sources to the DB.

## Tech Stack

- Database: PostgreSQL (with PostGIS extension)
- Backend + Web Server + API Server: Flask
- Frontend: HTML, React.js, Tailwind CSS, Leaflet.js 
- Version Control: Git + GitHub

## How to run

### Locally
Install PostgreSQL and PostGIS extension

Set up your `.env.local` file, you may refer to the `.env.docker` file included in the repo (it is stripped of sensitive data)

Modify scraper configs in `\backend\app\core\config.py` if required

In `\backend`:
1. `pip install -r requirements.txt` (if first time starting)
2. `python -m app.main`

Using another terminal, in `\frontend`
1. `npm install` (if first time starting)
2. `npm start`

Done! Open `localhost:3000` in your browser to view the webpage. For the API, send queries to `localhost:5000`.

### Docker container

Start up Docker Desktop

In the SeaSentry folder, run `docker compose up --build`

To stop, run `docker compose down`

## API Endpoints
All APIs are requested on localhost port 5000. Otherwise, CORS only allowed on http://localhost:3000 and http://127.0.0.1:3000 for the web application.

Fields are compulsory unless otherwise stated

### GET `/api/v1/vessels/bbox`

Summary: Query latest vessel positions within a bounding box

Returns:

- 200 with JSON with latest vessel location and details

- 400 if missing fields

- 500 if internal server error

Query Params:

- lat_min, lat_max, long_min, long_max: float (bounding box)

- time_within: int (optional, time in seconds, default 24hrs ie 60 * 60 * 24)

- limit: int (optional, default 50, max 1000)

E.g. `/api/v1/vessels/bbox?lat_min=1.2535&lat_max=1.2664&long_min=103.8233&long_max=103.8559&limit=25&time_within=670`

This will return the 25 latest vessel locations with its corresponding unique vessels within the given area in the past 670 seconds.

### GET `/api/v1/aois/get/all`

Summary: Query for all AOIs

Returns:

- 200 with JSON of all AOIs

- 500 if internal server error

### POST `/api/v1/aois/add/box`

Summary: Adds specified bounding box.

Returns:

- 201 if successfully added

- 400 if missing fields

- 500 if internal server error

Query Params:

- lat_min, lat_max, long_min, long_max: float (bounding box)

- name: str (name of AOI)

- desc: str (optional)
