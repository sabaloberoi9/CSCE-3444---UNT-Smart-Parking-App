# UNT Smart Parking App (NaVUNT)

An intelligent campus navigation and parking availability application built for University of North Texas (UNT) commuters[cite: 1, 2]. NaVUNT reduces parking congestion by monitoring real-time lot capacity, projecting availability with predictive modeling, and delivering seamless driving and walking navigation straight to class[cite: 1, 2].

---

## Overview

Finding open parking during peak campus hours at UNT frequently leads to delays, increased fuel consumption, and student stress[cite: 1]. NaVUNT eliminates the guesswork of finding an open spot by matching student schedules with dynamic lot availability, parking permit tiers, and proximity calculations[cite: 1, 2].

---

## Core Features

* **Authenticated Access:** Support for student and faculty login profiles to deliver personalized route and permit recommendations (FR-1)[cite: 2].
* **Class Schedule Integration:** Automatic extraction and display of upcoming classes and building locations from the user's schedule (FR-2, FR-3)[cite: 2].
* **Interactive Campus Map:** Campus visualization with lot markers and live occupancy status indicators (Available, Filling Up, Full) (FR-4)[cite: 2].
* **Real-Time Occupancy Metrics:** Continuous updates on space availability calculated from entry/exit events and sensor data (FR-5, FR-12)[cite: 2].
* **Dynamic Recommendation Engine:** Recommends optimal lots based on walking distance to class, spot availability, and permit eligibility (FR-6)[cite: 2].
* **Fallback Lot Routing:** Automatic alternative suggestions when a selected lot fills up before arrival (FR-11)[cite: 2].
* **Predictive Forecasting:** Pattern-based modeling forecasting lot full-times using historical data trends (FR-7)[cite: 2].
* **Multi-Modal Navigation:** Turn-by-turn driving directions to the chosen lot followed by pedestrian walking paths directly to destination classrooms (FR-8, FR-9)[cite: 2].
* **Community Updates & Alerts:** Student-submitted departure notices and automated alerts when favorite lots near capacity (FR-10, FR-13)[cite: 2].
* **Administrator Portal:** Dedicated console for UNT parking staff to manage lot capacities, record maintenance, and schedule closures (FR-14)[cite: 2].

---

## System Architecture

The project implements a 3-tier client-server architecture strictly enforcing downward-only dependencies[cite: 2]:

```text
+-------------------------------------------------------------+
|                     Presentation Layer                      |
|          Mobile Interface (React Native / Flutter)          |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                  API Gateway & Services                     |
|    Auth / Rate Limiting / Recommendation / OSRM Routing     |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                         Data Layer                          |
|         PostgreSQL / PostGIS / Historical Occupancy         |
+-------------------------------------------------------------+
```

1. **Presentation Layer:** User-facing mobile and administrative interfaces that communicate solely through the API gateway[cite: 2].
2. **API & Services Layer:** Manages authentication, lot ranking algorithms, third-party map integrations, and routing services[cite: 2].
3. **Data Layer:** Central data store managing spatial lot maps, user credentials, real-time sensor metrics, and occupancy logs[cite: 2].

---

## Repository Structure

```text
.
├── client/                 # Mobile application client source
│   ├── assets/             # Map icons, illustrations, and design assets
│   ├── src/
│   │   ├── components/     # Reusable UI widgets (Map overlays, Schedule cards)
│   │   ├── screens/        # Core screens (Home, Schedule, Maps, Forecast)
│   │   └── services/       # API integration and local storage
│   └── package.json
├── server/                 # Backend API services
│   ├── controllers/        # Route controllers (Auth, Parking, Navigation)
│   ├── models/             # Schema definitions and database models
│   ├── services/           # Recommendation algorithms and routing handlers
│   ├── utils/              # Token validation and security middleware
│   └── requirements.txt
├── database/               # Relational database configurations
│   ├── migrations/         # Table migration scripts
│   └── seeds/              # Mock campus coordinates, lots, and buildings
├── docs/                   # Software Requirements Specification (SRS) & diagrams
└── README.md
```

---

## Branching & Workflow Strategy

To maintain codebase stability, the repository follows standard Git branching conventions:

* **main:** Production branch containing tested, stable releases. Direct pushes are disabled.
* **dev:** Integration branch where all completed features are combined and tested.
* **feature/<task-name>:** Working branches branched from `dev` for specific tasks (for example, `feature/auth-endpoints`, `feature/map-view`).
* All code changes require a pull request into `dev` with at least one team member code review.

---

## Getting Started

### Prerequisites

* Git (v2.30+)
* Node.js (v18+) or Python (v3.10+)
* PostgreSQL with PostGIS extension enabled

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-org>/unt-smart-parking-app.git
   cd unt-smart-parking-app
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Add your local database credentials, JWT secret keys, and map service API endpoints.

3. **Install dependencies and start backend:**
   ```bash
   cd server
   pip install -r requirements.txt
   python main.py
   ```

4. **Start the client application:**
   ```bash
   cd ../client
   npm install
   npm start
   ```

---

## Team Members & Responsibilities

* **Dhanush Manjunath** - Architecture Design, Git Management & Backend Services[cite: 1]
* **Sabal Oberoi** - User Authentication, Security Protocols & Map Visualizations[cite: 1, 2]
* **Osamudiameh Okungbowa** - Class Schedule UI & Multi-Modal Routing[cite: 1, 2]
* **Jayla Whale** - Database Schemas, Data Seeding & Real-Time Alerts[cite: 1, 2]
