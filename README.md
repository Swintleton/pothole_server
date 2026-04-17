# Road Defect Mapping

This project presents a road defect mapping system built around artificial intelligence, a mobile client, and a server-side backend. Its goal is to detect potholes and other road defects from images and video frames, store their GPS coordinates in a central database, and display them on a map to support faster and more effective maintenance planning.

## Documentation

Complete project documentation is available in the [`documentation`](./documentation) folder.

For the detailed English documentation, see:
[`documentation_english.pdf`](https://github.com/Swintleton/pothole_server/blob/main/documentation/documentation_english.pdf)

A projekt részletesebb magyar nyelvű leírása itt érhető el:
[`documentation_hungarian_original.pdf`](https://github.com/Swintleton/pothole_server/blob/main/documentation/documentation_hungarian_original.pdf)

## Table of Contents

1. [Pothole Detection Server](#pothole-detection-server)
2. [What I Built](#what-i-built)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Features](#features)
6. [Development Setup](#development-setup)
7. [Running the Server](#running-the-server)
8. [API Overview](#api-overview)
9. [Testing and Logging](#testing-and-logging)
10. [Magyar változat](#magyar-változat)

---

# Pothole Detection Server

This repository contains the Flask-based backend of the Road Defect Mapping project. The server handles authentication, image upload, pothole-related data storage, map data retrieval, and the confirmation workflow for AI detections.

## What I Built

I built this project myself as part of my thesis work.

Within the full road defect mapping system, this repository is responsible for:

- authenticating users and handling role-based access,
- receiving uploaded image frames from the mobile client,
- storing pothole coordinates and related image metadata,
- serving pothole data for map-based visualization,
- processing confirmation workflows for AI-detected potholes,
- and supporting the detection pipeline used by the background detection daemon.

## Architecture

The full solution follows a client-server architecture:

- **Client:** a Flutter mobile application used for login, map interaction, camera capture, and detection confirmation
- **Server:** a Flask application that exposes HTTP endpoints and business logic
- **Database:** PostgreSQL for users, uploaded images, detection state, and pothole coordinates
- **Detection layer:** a YOLO-based background process that monitors uploaded frames and processes them separately from the web server

## Tech Stack

- **Backend / API:** Flask, Flask-CORS, Flask-JWT-Extended
- **Database:** PostgreSQL, psycopg2-binary
- **Machine Learning / Detection:** PyTorch, Torchvision, Ultralytics YOLO
- **Image Processing:** OpenCV, Pillow
- **Data Handling / Utilities:** NumPy, Pandas, Requests, PyYAML, tqdm
- **Visualization / Training Support:** Matplotlib

## Features

- User authentication and JWT-based access control
- Role handling for regular users and admins
- Frame upload with GPS coordinates from the mobile client
- Storage and retrieval of pothole coordinates
- Manual pothole creation and pothole editing
- Detection confirmation workflow for AI-processed images
- Image and detection state handling for uploaded frames
- Integration with a background detection daemon

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Swintleton/pothole_server.git
   cd pothole_server
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Optional Anaconda-based setup:

   ```bash
   conda create -n pothole-detector python=3.8
   conda activate pothole-detector
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**

   Create your PostgreSQL database, then load the schema from `server/db_changes.sql`.

   Example development setup used in the thesis:

   - Database name: `pothole`
   - User: `postgres`
   - Password: `123456`

4. **Configure the application**

   Update your configuration to match your local environment. For example, set the database connection and secret key in your config or environment variables.

## Running the Server

Start the Flask application:

```bash
python server.py
```

Start the detection daemon in a separate terminal:

```bash
cd server/yolov9
python daemon_detect.py
```

The detection daemon is responsible for watching incoming uploaded frames and processing pothole detections in the background.

## API Overview

Core endpoints used by the system:

### Authentication

- `POST /login`
- `POST /register`
- `POST /logout`

### Image upload and detection

- `POST /upload_frame`
- `GET /get_detection_confirmation`
- `GET /get_detected_image/<filename>`
- `POST /confirm`

### Pothole management

- `GET /potholes`
- `POST /add_pothole`
- `PUT /edit_pothole/<id>`
- `DELETE /delete_pothole/<id>`

## Testing and Logging

The thesis documentation describes unit and process-level tests for authentication, upload handling, pothole CRUD operations, and confirmation flows.

The server also writes logs not only to standard output but to `server/server.log` as well.

---

# Magyar változat

# Közúti hibák feltérképezése

A projekt egy mesterséges intelligenciára, egy mobil kliensalkalmazásra és egy szerveroldali háttérrendszerre épülő közúti hibafeltérképező megoldást mutat be. A cél az, hogy képekből és videóképkockákból felismerje a kátyúkat és egyéb úthibákat, a GPS-koordinátáikat egy központi adatbázisban tárolja, majd térképen megjelenítse őket, ezzel támogatva a gyorsabb és hatékonyabb karbantartási tervezést.

## Dokumentáció

A teljes projekt dokumentációja a [`documentation`](./documentation) mappában található.

A részletes angol nyelvű dokumentáció itt érhető el:
[`documentation_english.pdf`](https://github.com/Swintleton/pothole_server/blob/main/documentation/documentation_english.pdf)

A projekt részletesebb magyar nyelvű leírása itt érhető el:
[`documentation_hungarian_original.pdf`](https://github.com/Swintleton/pothole_server/blob/main/documentation/documentation_hungarian_original.pdf)

## Tartalomjegyzék

1. [Kátyúfelismerő szerver](#kátyúfelismerő-szerver)
2. [Mit készítettem](#mit-készítettem)
3. [Architektúra](#architektúra)
4. [Technológiai stack](#technológiai-stack)
5. [Funkciók](#funkciók)
6. [Fejlesztői környezet](#fejlesztői-környezet)
7. [A szerver indítása](#a-szerver-indítása)
8. [API áttekintés](#api-áttekintés)
9. [Tesztek és naplózás](#tesztek-és-naplózás)

---

# Kátyúfelismerő szerver

Ez a repository a Road Defect Mapping projekt Flask-alapú backendjét tartalmazza. A szerver hitelesítést, képfeltöltést, kátyúadat-kezelést, térképes adatlekérdezést és az AI által detektált találatok visszaigazolási folyamatát kezeli.

## Mit készítettem

A projektet saját magam készítettem a szakdolgozatom részeként.

A teljes közúti hibafeltérképező rendszeren belül ez a repository felel a következőkért:

- felhasználók hitelesítése és szerepköralapú jogosultságkezelése,
- képkockák fogadása a mobil kliensalkalmazástól,
- kátyúkoordináták és kapcsolódó képadatok tárolása,
- térképes megjelenítéshez szükséges adatok kiszolgálása,
- az AI által észlelt kátyúk visszaigazolási folyamatának kezelése,
- valamint a háttérben futó detektáló daemon kiszolgálása.

## Architektúra

A teljes megoldás kliens-szerver architektúrát követ:

- **Kliens:** Flutter alapú mobilalkalmazás bejelentkezéshez, térképes műveletekhez, kamerakép-feldolgozáshoz és visszaigazoláshoz
- **Szerver:** Flask alkalmazás HTTP végpontokkal és üzleti logikával
- **Adatbázis:** PostgreSQL a felhasználók, feltöltött képek, detektálási állapotok és kátyúkoordináták tárolására
- **Detektáló réteg:** YOLO-alapú háttérfolyamat, amely a feltöltött képkockákat a webszervertől elkülönítve dolgozza fel

## Technológiai stack

- **Backend / API:** Flask, Flask-CORS, Flask-JWT-Extended
- **Adatbázis:** PostgreSQL, psycopg2-binary
- **Gépi tanulás / detektálás:** PyTorch, Torchvision, Ultralytics YOLO
- **Képfeldolgozás:** OpenCV, Pillow
- **Adatkezelés / segédkönyvtárak:** NumPy, Pandas, Requests, PyYAML, tqdm
- **Vizualizáció / tréningtámogatás:** Matplotlib

## Funkciók

- Felhasználó-hitelesítés és JWT alapú hozzáférés-kezelés
- Szerepkörkezelés általános felhasználók és adminok számára
- GPS-koordinátákkal ellátott képkockák fogadása a mobil klienstől
- Kátyúkoordináták tárolása és lekérése
- Kézi kátyúfelvitel és meglévő kátyúk szerkesztése
- Visszaigazolási folyamat az AI által feldolgozott képekhez
- Feltöltött képek és detektálási állapotok kezelése
- Integráció a háttérben futó detektáló daemon folyamattal

## Fejlesztői környezet

1. **A repository klónozása**

   ```bash
   git clone https://github.com/Swintleton/pothole_server.git
   cd pothole_server
   ```

2. **Virtuális környezet létrehozása és a függőségek telepítése**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # vagy Windows esetén: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Opcionális Anaconda-alapú beállítás:

   ```bash
   conda create -n pothole-detector python=3.8
   conda activate pothole-detector
   pip install -r requirements.txt
   ```

3. **PostgreSQL beállítása**

   Hozd létre a PostgreSQL adatbázist, majd töltsd be a sémát a `server/db_changes.sql` fájlból.

   A szakdolgozatban használt példa fejlesztői beállítás:

   - Adatbázis neve: `pothole`
   - Felhasználó: `postgres`
   - Jelszó: `123456`

4. **Alkalmazás konfigurálása**

   Állítsd be a konfigurációt a saját környezetednek megfelelően. Például add meg az adatbázis-kapcsolatot és a titkos kulcsot a konfigurációban vagy környezeti változókban.

## A szerver indítása

A Flask alkalmazás indítása:

```bash
python server.py
```

A detektáló daemon indítása külön terminálban:

```bash
cd server/yolov9
python daemon_detect.py
```

A detektáló daemon feladata, hogy figyelje a beérkező képkockákat, és a háttérben feldolgozza a kátyúdetektálást.

## API áttekintés

A rendszer főbb végpontjai:

### Hitelesítés

- `POST /login`
- `POST /register`
- `POST /logout`

### Képfeltöltés és detektálás

- `POST /upload_frame`
- `GET /get_detection_confirmation`
- `GET /get_detected_image/<filename>`
- `POST /confirm`

### Kátyúkezelés

- `GET /potholes`
- `POST /add_pothole`
- `PUT /edit_pothole/<id>`
- `DELETE /delete_pothole/<id>`

## Tesztek és naplózás

A szakdolgozat dokumentációja egységteszteket és teljes folyamatokat szimuláló teszteket is ismertet a hitelesítéshez, a képfeltöltéshez, a kátyú CRUD műveletekhez és a visszaigazolási folyamathoz.

A szerver a naplókat nemcsak a standard kimenetre írja, hanem a `server/server.log` fájlba is.
