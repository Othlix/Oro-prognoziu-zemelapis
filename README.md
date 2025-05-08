# Oro prognozių žemėlapis

Šis projektas demonstruoja į paslaugą orientuotą architektūrą (SOA) naudojant Docker konteinerių platformą. Sistema leidžia vartotojams įvesti Lietuvos miestą ar vietovę ir gauti esamas bei būsimas oro prognozes.

## Sistemos architektūra

Sistema susideda iš trijų konteinerių, kurie sąveikauja tarpusavyje:

1. **WEB servisas** - pagrindinis konteineris, kuris valdo vartotojo sąsają ir orkestruoja kitas paslaugas
2. **Meteo servisas** - sąveikauja su meteo.lt API ir teikia orų prognozes
3. **NOMINATIM servisas** - tikrina vietovių pavadinimus ir formatuoja juos

### Duomenų srautas:

1. Vartotojas įveda miestą į web sąsają
2. WEB servisas kreipiasi į NOMINATIM servisą patikrinti vietovę
3. NOMINATIM servisas grąžina suformatuotą vietovės pavadinimą
4. WEB servisas kreipiasi į Meteo servisą gauti orų duomenis
5. Meteo servisas gauna duomenis iš meteo.lt API
6. Rezultatas grąžinamas vartotojui ir atvaizduojamas žemėlapyje

## Reikalavimai

- Docker
- Docker Compose

## Diegimas ir paleidimas

1. Klonuokite šį repozitoriumą:
   ```
   git clone https://github.com/jusername/oro-prognoziu-zemelapiai.git
   cd oro-prognoziu-zemelapiai
   ```

2. Paleiskite sistemą naudodami Docker Compose:
   ```
   docker-compose up --build
   ```

3. Atverkite naršyklę ir eikite į adresą:
   ```
   http://localhost:8000
   ```

## Naudojimas

1. Įveskite Lietuvos miesto ar vietovės pavadinimą į paieškos lauką
2. Spauskite "Ieškoti" arba paspauskite "Enter"
3. Jei vietovė rasta, žemėlapyje bus pažymėta jos vieta ir pateikta orų prognozė
4. Oro prognozėje matysite dabartinę temperatūrą, vėjo greitį ir kryptį, debesuotumą ir kitus parametrus
5. Taip pat matysite artimiausių dienų orų prognozes

## Pagrindinės technologijos

- **Flask** - Python web karkasas
- **Docker** - konteinerių platforma
- **Socket.IO** - realaus laiko duomenų perdavimui
- **Leaflet.js** - interaktyviam žemėlapiui
- **Bootstrap** - vartotojo sąsajos stilizavimui

## Išplėtimo galimybės

1. Pridėti daugiau oro prognozės parametrų vizualizaciją
2. Įgyvendinti vartotojų autentifikaciją ir galimybę išsaugoti mėgstamas vietas
3. Pridėti kelių dienų orų prognozių diagramas
4. Automatiškai atnaujinti duomenis be puslapio perkrovimo

## API apžvalga

### WEB servisas (localhost:8000)
- `GET /` - Pagrindinis puslapis
- `POST /api/weather` - Gauti oro prognozės duomenis (reikalauja `city` parametro)

### Meteo servisas (vidinis tinklas)
- `POST /weather` - Gauti orų prognozes iš meteo.lt API (reikalauja `place_name` parametro)

### NOMINATIM servisas (vidinis tinklas)
- `POST /validate` - Patikrinti ir formatuoti vietovę (reikalauja `query` parametro)
