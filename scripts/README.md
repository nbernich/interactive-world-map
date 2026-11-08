# Compiling Data From Sources

Compiling requires the Python language. Install at: `https://www.python.org/`. Any recent version should do.

## Country Data

Country data (information, flags, geographic shape) comes from: `https://github.com/mledoze/countries` (license: Open Data Commons Open Database License (ODbL) v1.0)

1. Navigate to the `data` folder (which this file is in):

```bash
cd ./scripts
```

2. Clone the repository:

```bash
git clone https://github.com/mledoze/countries.git
```

3. Run the compilation script:

```bash
python compile_country_data.py
```

4. The script will automatically create `countries.json` in the `public/data` folder of the Node/React.js project! You are free to delete the cloned repository (it wll also be gitignored).

## Flight Data (Airports and Routes)

Airport and routes data comes from: `https://airportmiles.com/` ([licenses](https://airportmiles.com/sources))

1. Navigate to the `scripts` folder, if you haven't already:

```bash
cd ./scripts
```

2. Ensure the `requests` library is installed:

```bash
pip install requests
```

or:

```bash
pip install -r requirements.txt
```

3. Run the compilation script:

```bash
python compile_airport_data.py
```

4. The script will automatically create `airports.json` and `routes.json` in the `public/data` folder of the Node/React.js project! No intermediate files need to be deleted; the requested source data is in-memory only.
