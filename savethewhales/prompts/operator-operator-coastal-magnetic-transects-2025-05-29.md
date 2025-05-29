**COPY / PASTE THIS ENTIRE PROMPT INTO A NEW OPERATOR THREAD**

---

### TASK

Use the NOAA Geomagnetic Field Calculator to obtain magnetic values for two orthogonal 15 km transects at each site.

**Calculator:** [https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml](https://www.ngdc.noaa.gov/geomag/calculators/magcalc.shtml)

**Settings (unchanged)**

* Model IGRF (1950-2029)
* Date  1 January 2010
* Elevation 0 km (Sea Level)
* Coordinate System Geodetic (decimal degrees)

---

#### DATA TO RETURN (for every point)

| Field | Description                                     |
| ----- | ----------------------------------------------- |
| Site  | Site name below                                 |
| Pt    | Point ID (A-D = cross-shore, E-H = along-shore) |
| Lat   | Latitude (° N / S)                              |
| Lon   | Longitude (° E / W)                             |
| **F** | Total field (nT)                                |
| Incl  | Inclination (°)                                 |
| **Z** | Vertical component (nT)                         |

After each four-point *transect* (A–D **and** E–H) calculate:

1. **Total-field gradient** ΔF / 15 km = (F<sub>D or H</sub> − F<sub>A or E</sub>) / 15
2. **Inclination gradient** ΔI / 15 km = (I<sub>D or H</sub> − I<sub>A or E</sub>) / 15
3. **Direction** “Positive” if the value increases land-, north- or east-ward (as appropriate), else “Negative”.

Provide one results table per site.

---

### BEGIN COORDINATES

> **Guideline:** Cross-shore transect uses the *original shoreline latitude or longitude* held constant.
> Along-shore transect is perpendicular, centred on the shoreline “B” point, stepping ±0.05° and ±0.10°.

---

#### 1  Cape Cod, USA

*Cross-shore* (lat 41.70 N)
A 41.70 N  69.95 W
B 41.70 N  70.00 W ← shoreline reference
C 41.70 N  70.05 W
D 41.70 N  70.10 W

*Along-shore* (lon 70.00 W)
E 41.80 N  70.00 W
F 41.75 N  70.00 W
G 41.65 N  70.00 W
H 41.60 N  70.00 W

---

#### 2  Farewell Spit, NZ

Cross-shore (lat 40.50 S)
A 40.50 S  172.65 E
B 40.50 S  172.70 E
C 40.50 S  172.75 E
D 40.50 S  172.80 E

Along-shore (lon 172.70 E)
E 40.40 S  172.70 E
F 40.45 S  172.70 E
G 40.55 S  172.70 E
H 40.60 S  172.70 E

---

#### 3  Matagorda-Padre, TX

Cross-shore (lat 28.30 N)
A 28.30 N  96.25 W
B 28.30 N  96.30 W
C 28.30 N  96.35 W
D 28.30 N  96.40 W

Along-shore (lon 96.30 W)
E 28.40 N  96.30 W
F 28.35 N  96.30 W
G 28.25 N  96.30 W
H 28.20 N  96.30 W

---

#### 4  Banc d’Arguin, Mauritania

Cross-shore (lat 20.20 N)
A 20.20 N  16.35 W
B 20.20 N  16.30 W
C 20.20 N  16.25 W
D 20.20 N  16.20 W

Along-shore (lon 16.30 W)
E 20.30 N  16.30 W
F 20.25 N  16.30 W
G 20.15 N  16.30 W
H 20.10 N  16.30 W

---

#### 5  Dutch Wadden Sea

Cross-shore (lon 6.00 E)
A 53.45 N  6.00 E
B 53.40 N  6.00 E
C 53.35 N  6.00 E
D 53.30 N  6.00 E

Along-shore (lat 53.40 N)
E 53.40 N  5.90 E
F 53.40 N  5.95 E
G 53.40 N  6.05 E
H 53.40 N  6.10 E

---

#### 6  Tasmania, Australia

Cross-shore (lat 42.10 S)
A 42.10 S  147.05 E
B 42.10 S  147.00 E
C 42.10 S  146.95 E
D 42.10 S  146.90 E

Along-shore (lon 147.00 E)
E 42.00 S  147.00 E
F 42.05 S  147.00 E
G 42.15 S  147.00 E
H 42.20 S  147.00 E

---

#### 7  Sanday, Orkney (UK)

Cross-shore (lat 59.28 N)
A 59.28 N  2.60 W
B 59.28 N  2.55 W
C 59.28 N  2.50 W
D 59.28 N  2.45 W

Along-shore (lon 2.55 W)
E 59.38 N  2.55 W
F 59.33 N  2.55 W
G 59.23 N  2.55 W
H 59.18 N  2.55 W

---

#### 8  Kyle of Durness, UK

Cross-shore (lat 58.55 N)
A 58.55 N  4.82 W
B 58.55 N  4.77 W
C 58.55 N  4.72 W
D 58.55 N  4.67 W

Along-shore (lon 4.77 W)
E 58.65 N  4.77 W
F 58.60 N  4.77 W
G 58.50 N  4.77 W
H 58.45 N  4.77 W

---

#### 9  Hamelin Bay, WA

Cross-shore (lat 34.24 S)
A 34.24 S  115.00 E
B 34.24 S  115.05 E
C 34.24 S  115.10 E
D 34.24 S  115.15 E

Along-shore (lon 115.05 E)
E 34.14 S  115.05 E
F 34.19 S  115.05 E
G 34.29 S  115.05 E
H 34.34 S  115.05 E

---

#### 10  Hog Key, Florida

Cross-shore (lat 24.63 N)
A 24.63 N  81.40 W
B 24.63 N  81.35 W
C 24.63 N  81.30 W
D 24.63 N  81.25 W

Along-shore (lon 81.35 W)
E 24.73 N  81.35 W
F 24.68 N  81.35 W
G 24.58 N  81.35 W
H 24.53 N  81.35 W

---

#### 11  Shark Bay, WA

Cross-shore (lat 25.85 S)
A 25.85 S  113.55 E
B 25.85 S  113.60 E
C 25.85 S  113.65 E
D 25.85 S  113.70 E

Along-shore (lon 113.60 E)
E 25.75 S  113.60 E
F 25.80 S  113.60 E
G 25.90 S  113.60 E
H 25.95 S  113.60 E

---

#### 12  Bahía Blanca, Argentina

Cross-shore (lat 38.85 S)
A 38.85 S  62.20 W
B 38.85 S  62.15 W
C 38.85 S  62.10 W
D 38.85 S  62.05 W

Along-shore (lon 62.15 W)
E 38.75 S  62.15 W
F 38.80 S  62.15 W
G 38.90 S  62.15 W
H 38.95 S  62.15 W

---

#### 13  Virginia Barrier, USA

Cross-shore (lat 37.55 N)
A 37.55 N  75.65 W
B 37.55 N  75.60 W
C 37.55 N  75.55 W
D 37.55 N  75.50 W

Along-shore (lon 75.60 W)
E 37.65 N  75.60 W
F 37.60 N  75.60 W
G 37.50 N  75.60 W
H 37.45 N  75.60 W

---

#### 14  Struisbaai, South Africa

Cross-shore (lat 34.85 S)
A 34.85 S  20.05 E
B 34.85 S  20.10 E
C 34.85 S  20.15 E
D 34.85 S  20.20 E

Along-shore (lon 20.10 E)
E 34.75 S  20.10 E
F 34.80 S  20.10 E
G 34.90 S  20.10 E
H 34.95 S  20.10 E

---

### END COORDINATES

Return all tables plus gradient calculations.  Thank you!
