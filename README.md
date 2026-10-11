# Cajander Forest Matrix Classifier (QGIS Plugin)

A high-performance QGIS plugin designed for **automated forest biome classification** using satellite imagery (Sentinel-2) and digital elevation models (Copernicus DEM). The core analytical engine replicates the Cajander forest site type classification system by analyzing multi-spectral indices, soil moisture patterns, and terrain morphometry.

<p align="center">
  <img src="images/screenshot1.png" width="45%" alt="Biome Classification Tab" />
  <img src="images/screenshot2.png" width="45%" alt="Index Preparation Tab" />
</p>

## 🚀 Key Features & Domain Logic

*   **Multi-Spectral & Morphometric Analysis**: Evaluates raw satellite bands and calculated indices across multiple dimensions:
    *   *Vegetation Indices*: NDVI (Spring/Summer), NDRE (Chlorophyll/RedEdge).
    *   *Moisture Indices*: NDWI (Vegetation liquid water), NDII (Moisture intensity).
    *   *Terrain Morphometry*: Slope analysis and Topographic Wetness Index (TWI) derived from Digital Elevation Models (DEM).
*   **Decoupled State Management**: Advanced UI built with PyQt/PySide that dynamically maps spatial parameters, threshold selections, and raster layer dependencies without locking the QGIS main thread.

## 🏗️ Architectural & Engineering Highlights

This project was built with strict adherence to professional software engineering patterns, moving away from the typical monolithic script approach found in many GIS utilities:

### ⚡ The "Sieve" Pipeline (NumPy Vectorization)
To process heavy raster datasets efficiently without memory bottlenecks, the plugin utilizes a **Pipeline / Chain of Responsibility** pattern driven entirely by **NumPy vector computations**:
1.  The orchestrator initializes a high-performance memory grid matching the target bounding box and resolution.
2.  Data runs through independent, decoupled classification modules (e.g., `classify_biome_400` for open sphagnum bogs).
3.  Each module fetches only its required spectral bands or indices via a dedicated Data Service, applies lightning-fast mask operations, and modifies the state matrix. This allows adding new biomes or shifting criteria without core refactoring.

### 🧩 Clean Architecture & Dependency Injection
*   **Separation of Concerns (SoC)**: Complete isolation between QGIS GUI components, data access layers, and pure domain classification logic.
*   **Explicit Dependency Injection**: Business logic components receive spatial services and raster providers via DI, ensuring the analytical core remains highly testable and maintainable.
*   **Hot Module Replacement (HMR) for Debugging**: Includes a custom-built runtime cache-busting mechanism (`sys.modules` reset) allowing continuous development and live UI/logic updates directly inside QGIS without restarting the desktop application.

## 📊 Data Requirements

The plugin is designed to seamlessly integrate with open enterprise spatial data. It targets and runs vector calculations on pre-loaded project layers containing:
*   **Sentinel-2** multi-spectral imagery (specifically targeting March B04, May NDWI, July NDVI/NDRE/NDII).
*   **Copernicus DEM** (or any valid regional Digital Elevation Model) for computing slope and hydrological TWI grids.

## 🛠️ Tech Stack

*   **Host Environment**: QGIS 3.x API
*   **Language**: Python 3
*   **GUI Framework**: PyQt / PySide
*   **Math & Data Science**: NumPy
