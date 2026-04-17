# Road Defect Mapping

This project focuses on the development of an artificial intelligence-based object detection system capable of automatically analyzing videos and images to identify road defects such as potholes.

The system records the GPS coordinates of the detected road defects and stores them in a central database. Using the data collected in this database, the system can display the exact locations of road defects on a map, enabling more efficient planning and execution of road maintenance and repair work.

## Documentation

Complete documentation can be found in the [`documentation`](./documentation) folder.

For a more detailed English description of the full project, see the complete documentation here:
[`documentation_english.pdf`](https://github.com/Swintleton/pothole_server/blob/main/documentation/documentation_english.pdf)

## Table of Contents

1. [Pothole Detection Server](#pothole-detection-server)
2. [What I Built](#what-i-built)
3. [Tech Stack](#tech-stack)
4. [Features](#features)
5. [Requirements](#requirements)
6. [Installation](#installation)
7. [Usage](#usage)
8. [Endpoints](#endpoints)
9. [Troubleshooting and FAQ](#troubleshooting-and-faq)
10. [Magyar változat](#magyar-változat)

---

# Pothole Detection Server

This repository contains the Flask-based server application for the pothole detection system. It supports image processing, data management, user authentication, coordinate handling, and user confirmation workflows.

## What I Built

I built this project myself as part of a larger road defect mapping system.

The server is responsible for:

- authenticating users and handling access control,
- receiving uploaded images from the client application,
- running pothole detection-related processing,
- storing and editing pothole coordinates in a PostgreSQL database,
- serving pothole data for map-based visualization,
- and handling user confirmations for detected potholes.

## Tech Stack

The project uses the following stack:

- **Backend / API**: Flask, Flask-CORS, Flask-JWT-Extended
- **Database**: PostgreSQL, psycopg2-binary
- **Machine Learning / Detection**: PyTorch, Torchvision, Ultralytics YOLO
- **Image Processing**: OpenCV, Pillow
- **Data Handling**: NumPy, Pandas
- **Visualization / Utilities**: Matplotlib, tqdm, PyYAML, Requests

## Features

- User authentication and role management for administrators and general users.
- Image upload from the client-side application.
- Processing of image-based pothole detection.
- Saving and editing the coordinates of pothole locations.
- Handling user confirmations for detected pothole locations.

## Requirements

- Python 3.8 or later
- PostgreSQL database
- Required Python packages listed in the `requirements.txt` file

## Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd server
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # on Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the database**
   Create a PostgreSQL database and load the database schema:

   ```sql
   CREATE DATABASE pothole_detection;
   \c pothole_detection
   -- Load the database schema if a corresponding .sql file is provided
   ```

4. **Configure environment variables**
   Modify `config.py`, or create a `.env` file in the project root and define the following environment variables:

   ```plaintext
   FLASK_ENV=production
   DATABASE_URL=postgresql://<username>:<password>@localhost:5432/pothole_detection
   SECRET_KEY=<secret_key>
   ```

5. **Run the server**
   Use the following command to start the server:

   ```bash
   python server.py
   ```

## Usage

The server runs on `localhost:5000`. The client-side application communicates with this server so users can log in, upload images, display pothole locations, and confirm detections.

## Endpoints

### Authentication Endpoints

- **POST /login**: User login  
  - **Request body**: `{ "username": "user", "password": "pass" }`
  - **Response**: A JWT token on successful login

- **POST /logout**: User logout  
  - Invalidates the token

### Image Upload Endpoint

- **POST /upload_frame**: Upload an image from the client to the server  
  - **Request body**: File and coordinates (`latitude`, `longitude`)
  - **Response**: `200 OK` if processing is successful

### Pothole Data Endpoints

- **GET /potholes**: Retrieve all pothole coordinates and related information  
  - **Response**: A list of potholes in JSON format

- **POST /add_pothole**: Add a new pothole manually  
  - **Request body**: `{ "latitude": <lat>, "longitude": <long> }`

- **PUT /edit_pothole/<id>**: Edit an existing pothole entry  
  - **Request body**: New coordinates and/or filenames

### Confirmation Endpoint

- **POST /confirm**: User confirmation for a detected pothole  
  - **Request body**: `{ "filename": "example.jpg", "confirmed": true }`

## Troubleshooting and FAQ

- **Error**: `ModuleNotFoundError`  
  - **Solution**: Make sure all required packages are installed using `pip install -r requirements.txt`.

- **Error**: `psycopg2.errors.UndefinedTable`  
  - **Solution**: Check whether the database has been initialized properly and whether the tables were created.

- **Error**: Flask does not start  
  - **Solution**: Verify that all required environment variables are correctly set in the `.env` file and that `SECRET_KEY` is strong and unique.

---

# Magyar változat

# Közúti hibák feltérképezése

A projekt egy mesterséges intelligencián alapuló objektumdetektáló rendszer fejlesztésével foglalkozik, amely képes videófelvételek és képek automatikus elemzésére úthibák, például kátyúk azonosítására.

A rendszer a detektált úthibák GPS-koordinátáit rögzíti, majd ezeket egy központi adatbázisban gyűjti össze. Az adatbázis tartalmát felhasználva a rendszer térképen képes megjeleníteni az úthibák pontos helyzetét, lehetővé téve ezzel az útjavítási munkálatok hatékonyabb tervezését és végrehajtását.

## Dokumentáció

A teljes dokumentáció a [`documentation`](./documentation) mappában található.

A projekt részletesebb angol nyelvű leírása itt érhető el:
[`documentation_english.pdf`](https://github.com/Swintleton/pothole_server/blob/main/documentation/documentation_english.pdf)

## Tartalomjegyzék

1. [Kátyúfelismerő szerver](#kátyúfelismerő-szerver)
2. [Mit készítettem](#mit-készítettem)
3. [Technológiai stack](#technológiai-stack)
4. [Funkciók](#funkciók)
5. [Követelmények](#követelmények)
6. [Telepítés](#telepítés)
7. [Használat](#használat)
8. [Végpontok](#végpontok)
9. [Hibakeresés és gyakori kérdések](#hibakeresés-és-gyakori-kérdések)

---

# Kátyúfelismerő szerver

Ez a repository a kátyúfelismerő rendszer Flask-alapú szerveralkalmazását tartalmazza. A szerver képfeldolgozást, adatkezelést, felhasználói hitelesítést, koordinátakezelést és felhasználói visszaigazolási folyamatokat támogat.

## Mit készítettem

Ezt a projektet saját magam készítettem egy nagyobb közúti hibafeltérképező rendszer részeként.

A szerver feladatai:

- felhasználók hitelesítése és jogosultságkezelése,
- képek fogadása a kliensalkalmazástól,
- kátyúdetektáláshoz kapcsolódó feldolgozás futtatása,
- a kátyúk koordinátáinak tárolása és szerkesztése PostgreSQL adatbázisban,
- térképes megjelenítéshez szükséges adatok kiszolgálása,
- valamint a felhasználói visszaigazolások kezelése a detektált kátyúkhoz.

## Technológiai stack

A projekt a következő technológiákat használja:

- **Backend / API**: Flask, Flask-CORS, Flask-JWT-Extended
- **Adatbázis**: PostgreSQL, psycopg2-binary
- **Gépi tanulás / detektálás**: PyTorch, Torchvision, Ultralytics YOLO
- **Képfeldolgozás**: OpenCV, Pillow
- **Adatkezelés**: NumPy, Pandas
- **Vizualizáció / segédkönyvtárak**: Matplotlib, tqdm, PyYAML, Requests

## Funkciók

- Felhasználó hitelesítés és szerepkörkezelés adminisztrátorok és általános felhasználók számára.
- Képfeltöltés a kliensoldali alkalmazásból.
- Kép alapú kátyúdetektálás feldolgozása.
- Kátyúhelyzetek koordinátáinak mentése és szerkesztése.
- Felhasználói visszaigazolások kezelése a detektált kátyúhelyekhez.

## Követelmények

- Python 3.8 vagy újabb
- PostgreSQL adatbázis
- A szükséges Python csomagok a `requirements.txt` fájlban vannak megadva

## Telepítés

1. **A repository klónozása**

   ```bash
   git clone <repository-url>
   cd server
   ```

2. **Virtuális környezet létrehozása és a függőségek telepítése**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # vagy Windows esetén: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Adatbázis beállítása**  
   Hozz létre egy PostgreSQL adatbázist, és töltsd be az adatbázis sémát:

   ```sql
   CREATE DATABASE pothole_detection;
   \c pothole_detection
   -- Töltsd be az adatbázis sémáját, ha van hozzá tartozó .sql fájl
   ```

4. **Környezetváltozók beállítása**  
   Módosítsd a `config.py` fájlt, vagy hozz létre egy `.env` fájlt a projekt gyökerében, és add meg a következő környezetváltozókat:

   ```plaintext
   FLASK_ENV=production
   DATABASE_URL=postgresql://<felhasználó>:<jelszó>@localhost:5432/pothole_detection
   SECRET_KEY=<titkos_kulcs>
   ```

5. **Indítás**  
   A szerver futtatásához használd a következő parancsot:

   ```bash
   python server.py
   ```

## Használat

A szerver a `localhost:5000` porton fut. A kliensoldali alkalmazás ezzel a szerverrel kommunikál, hogy a felhasználók bejelentkezzenek, képeket töltsenek fel, valamint megjelenítsék és megerősítsék a kátyúhelyzeteket.

## Végpontok

### Hitelesítési végpontok

- **POST /login**: Felhasználói bejelentkezés  
  - **Kérelmi törzs**: `{ "username": "user", "password": "pass" }`
  - **Válasz**: Sikeres bejelentkezés esetén egy JWT token

- **POST /logout**: Kijelentkezés  
  - A token érvénytelenítése

### Képfeltöltési végpont

- **POST /upload_frame**: Kép feltöltése a kliensoldalról a szerverre  
  - **Kérelmi törzs**: Fájl és koordináták (`latitude`, `longitude`)
  - **Válasz**: `200 OK` státusz sikeres feldolgozás esetén

### Kátyúadat-végpontok

- **GET /potholes**: Az összes kátyú koordinátájának és információjának lekérése  
  - **Válasz**: Kátyúk listája JSON formátumban

- **POST /add_pothole**: Új kátyú manuális hozzáadása  
  - **Kérelmi törzs**: `{ "latitude": <lat>, "longitude": <long> }`

- **PUT /edit_pothole/<id>**: Meglévő kátyú adatainak szerkesztése  
  - **Kérelmi törzs**: Új koordináták és/vagy fájlnevek

### Visszaigazolási végpont

- **POST /confirm**: Felhasználói visszaigazolás egy detektált kátyúról  
  - **Kérelmi törzs**: `{ "filename": "example.jpg", "confirmed": true }`

## Hibakeresés és gyakori kérdések

- **Hiba**: `ModuleNotFoundError`  
  - **Megoldás**: Győződj meg arról, hogy az összes szükséges csomag telepítve van a `pip install -r requirements.txt` paranccsal.

- **Hiba**: `psycopg2.errors.UndefinedTable`  
  - **Megoldás**: Ellenőrizd, hogy az adatbázis megfelelően inicializálva van-e, és a táblák létrejöttek-e.

- **Hiba**: A Flask nem indul el  
  - **Megoldás**: Ellenőrizd, hogy a `.env` fájlban minden szükséges környezetváltozó megfelelően van beállítva, és hogy a `SECRET_KEY` erős és egyedi.
