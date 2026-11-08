from __future__ import annotations
from typing import Any, TypedDict, List, Dict
import logging
import json
import os

COUNTRIES_FOLDER = os.path.join("countries",)
COUNTRIES_INFO_FILE = os.path.join(COUNTRIES_FOLDER, "dist", "countries-unescaped.json")
COUNTRIES_GEO_AND_FLAG_DIR = os.path.join(COUNTRIES_FOLDER, "data")

PUBLIC_DATA_PATH = os.path.join("..", "public", "data")
COMPILED_COUNTRIES_PATH = os.path.join(PUBLIC_DATA_PATH, "countries.json")

CountryCode = str

class Country(TypedDict):
  commonName: str
  officialName: str
  cca2: str
  latitude: float
  longitude: float
  region: str
  subregion: str
  capital: List[str]
  area: float
  borders: List[CountryCode]
  isIndependent: bool
  isUnMember: bool
  isLandlocked: bool
  languages: List[Language]
  currencies: List[Currency]
  tlds: List[str]
  idds: List[IDD]
  flagEmoji: str
  flagSvg: str
  renderData: RenderData

class Currency(TypedDict):
  name: str
  code: str
  symbol: str

class IDD(TypedDict):
  root: str
  suffixes: List[str]

class Language(TypedDict):
  name: str
  code: str

class RenderData(TypedDict):
  type: str
  features: List[Feature] 


class Feature(TypedDict):
  type: "Feature"
  properties: Dict[str, Any] | None
  geometry: Dict[str, Geometry]

class Geometry(TypedDict):
  type: str
  coordinates: Any # deeply nested lists

def main():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
  )

  if not os.path.exists(COUNTRIES_FOLDER):
    raise RuntimeError("Clone the countries repository first! See README.md for more details.")

  with open(COUNTRIES_INFO_FILE, "r", encoding="utf-8") as file:
    src_countries = json.load(file)

  compiled_countries_map: Dict[CountryCode, Country] = {}
  for country in src_countries:
    country_name = country["name"]["common"]
    cca3 = country["cca3"].upper()
    cca3_lower = cca3.lower()

    geo_file_path = os.path.join(COUNTRIES_GEO_AND_FLAG_DIR, f"{cca3_lower}.geo.json")
    if not os.path.exists(geo_file_path):
      raise RuntimeError(f"Missing geo file for {cca3} ({country_name}) at {geo_file_path}")

    with open(geo_file_path, "r", encoding="utf-8") as geo_file:
      render_data = json.load(geo_file)

    flag_file_path = os.path.join(COUNTRIES_GEO_AND_FLAG_DIR, f"{cca3_lower}.svg")
    if not os.path.exists(flag_file_path):
      raise RuntimeError(f"Missing flag file for {cca3} ({country_name}) at {flag_file_path}")

    with open(flag_file_path, "r", encoding="utf-8") as flag_file:
      flag_svg = flag_file.read()

    compiled_country: Country = {
      "commonName": country["name"]["common"],
      "officialName": country["name"]["official"],
      "cca2": country["cca2"],
      "latitude": country["latlng"][0],
      "longitude": country["latlng"][1],
      "region": country["region"],
      "subregion": country["subregion"],
      "capital": country["capital"],
      "area": country["area"],
      "borders": country["borders"],
      "isIndependent": country["independent"],
      "isUnMember": country["unMember"],
      "isLandlocked": country["landlocked"],
      "languages": [
        {"name": name, "code": code}
        for code, name in country["languages"].items()
      ],
      "currencies": [
        {"name": currency["name"], "code": code, "symbol": currency["symbol"]}
        for code, currency in country["currencies"].items()
      ],
      "flagEmoji": country["flag"],
      "tlds": country["tld"],
      "idds": [
        {"root": country["idd"]["root"], "suffixes": country["idd"]["suffixes"]}
      ],
      "flagSvg": flag_svg,
      "renderData": render_data
    }

    compiled_countries_map[cca3] = compiled_country
    logging.info("Compiled geographic data and flag SVG for %s (%s)", country_name, cca3)

  if not os.path.exists(PUBLIC_DATA_PATH):
    os.makedirs(PUBLIC_DATA_PATH)

  with open(COMPILED_COUNTRIES_PATH, "w", encoding="utf-8") as output_file:
    json.dump(compiled_countries_map, output_file, ensure_ascii=False, indent=2)

  logging.info("Compiled country data written to %s", COMPILED_COUNTRIES_PATH)

if __name__ == "__main__":
  main()