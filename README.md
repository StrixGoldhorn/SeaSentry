# Project SeaSentry

## Table of Contents
- [Project SeaSentry](#project-seasentry)
  - [Table of Contents](#table-of-contents)
  - [Motivation](#motivation)
  - [Aim](#aim)
  - [Tech Stack](#tech-stack)
  - [How to run](#how-to-run)
    - [Locally](#locally)
    - [Docker container](#docker-container)
  - [API Endpoints](#api-endpoints)


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

In `\backend`:
1. `pip install -r requirements.txt`
2. `playwright install`
3. `python -m app.main`

Using another terminal, go to `\frontend`
1. `npm start`

### Docker container

Start up Docker Desktop

In the SeaSentry folder, run `docker compose up --build`

To stop, run `docker compose down`

## API Endpoints
All APIs are requested on localhost port 5000. Otherwise, CORS only allowed on http://localhost:3000 and http://127.0.0.1:3000 for the web application.

Refer to [API Docs](./API_Docs.md) for the documentation.
