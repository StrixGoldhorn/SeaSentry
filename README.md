@ -4,43 +4,55 @@

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
Set up your `.env.local` file, you may refer to the `.env.docker` file included in the repo (it is stripped of sensitive data)

In `\backend`:
1. `pip install -r requirements.txt` (if first time starting)
2. `playwright install` (if first time starting)
3. `python -m app.main`

Using another terminal, in `\frontend`
1. `npm init` (if first time starting)
2. `npm install` (if first time starting)
3. `npm start`

### Docker container

Start up Docker Desktop

In the SeaSentry folder, run `docker compose up --build`

To stop, run `docker compose down`