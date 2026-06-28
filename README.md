# Project SeaSentry

# Table of Contents
- [Project SeaSentry](#project-seasentry)
- [Table of Contents](#table-of-contents)
- [Motivation](#motivation)
- [Aim](#aim)
- [Tech Stack](#tech-stack)
- [How to run](#how-to-run)
  - [Docker (Strongly Recommended)](#docker-strongly-recommended)
  - [Locally](#locally)
    - [Database](#database)
    - [Backend](#backend)
    - [Frontend](#frontend)
- [API Endpoints](#api-endpoints)


# Motivation 

Maritime traffic data is currently spread out across multiple sites, each with differing coverage, with limited options for free tiers (eg unable to view historical data for vessels , paywall for specific vessel details, etc.). SeaSentry acts as a data aggregator, scraping and combining data from multiple different sources to get a unified view, combining the data gained from various different sources into a locally hosted API. This allows users to freely track and record historical data of vessels without having to pay. Exposing our own API will allow users to better make use of the data in different ways, be it via plugins or integrating it into their own applications.


# Aim 

We hope to build a locally hosted server that provides an API endpoint and a UI where users can query for data such as current location, historical tracks, etc of different vessels.

Additional features such as geofencing, alerts, specific vessel tracking may follow later.

In the backend, the application will be scraping data from different sites and formatting and inserting the details into a database that the user controls.

We aim to provide a plugin based system for data sources, to allow users to add their own data sources to the DB.

# Tech Stack

- Database: PostgreSQL (with PostGIS extension)
- Backend + Web Server + API Server: Flask
- Frontend: HTML, React.js, Tailwind CSS, Leaflet.js 
- Version Control: Git + GitHub

# How to run

## Docker (Strongly Recommended)

If this is your first time, you have to install Docker first.

1. Ensure you have started Docker Desktop
2. In the SeaSentry folder, run `docker compose build`
3. In the SeaSentry folder, run `docker compose up`
4. After it finishes starting,
  - Access http://127.0.0.1:3000/ for the frontend
  - Access the API via http://127.0.0.1:5000/ 
5. To stop the service, run `docker compose down`


## Locally
After you start the backend and frontend services,
- Access http://127.0.0.1:3000/ for the frontend
- Access the API via http://127.0.0.1:5000/ 


### Database
YOU MUST DELETE THE EXISTING DATABASE, BREAKING CHANGES WERE MADE (If unsure, just drop all tables.)

If this is your first time, install PostgreSQL and the PostGIS extension

### Backend
All commands are to be performed in the SeaSentry/backend folder.
1. (Optional, recommended) Create a virtual environment and activate it.
2. `pip install -r requirements.txt` to install required packages
3. If you have not installed Playwright, run `playwright install` after step 2.
4. If the database has not been set up, in the SeaSentry/backend directory, run `python -m app.firsttime`
5. Adjust any params required in SeaSentry/backend/app/core/config.py
6. Set up your SeaSentry/.env.local
  - You can copy most of the info from .env.docker
  - You have to change the POSTGRES_HOST value to localhost
  - You have to change the POSTGRES_USER and POSTGRES_PASSWORD to your own Postgres username and password
7. Run `python -m app.main` to start the scraping and API service

### Frontend
All commands are to be performed in the SeaSentry/frontend folder.
1. `npm install`
2. Run `npm start` to start the frontend service


# API Endpoints
All APIs are accessed via localhost port 5000. Otherwise, CORS only allowed on http://localhost:3000 and http://127.0.0.1:3000 for the web application.

Refer to [API Docs](./API_Docs.md) for the documentation.
