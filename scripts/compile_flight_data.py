from __future__ import annotations

import requests

from typing import Dict, List, TypedDict
import logging
import json
import os

AIRPORTS_URL = "https://airportmiles.com/api/v1/airports.json"
ROUTES_URL = "https://airportmiles.com/api/v1/routes.json"

PUBLIC_DATA_PATH = os.path.join("..", "public", "data")
COMPILED_AIRPORTS_PATH = os.path.join(PUBLIC_DATA_PATH, "airports.json")
COMPILED_ROUTES_PATH = os.path.join(PUBLIC_DATA_PATH, "routes.json")

AirportCode = str
RouteCode = str # format ARRIVAL-DEPARTURE

class Airport(TypedDict):
  name: str
  municipality: str
  city: str | None
  cityCode: str
  country: str
  region: str | None
  latitude: float
  longitude: float
  size: str # small, medium, large...
  elevationMeters: float
  routeArrivals: List[RouteCode]
  routeDepartures: List[RouteCode]

class Route(TypedDict):
  departureAirport: AirportCode
  arrivalAirport: AirportCode
  distanceKm: float
  greatCircleKm: float
  flightTimeEstimateMin: float
  passengerCount: int
  seatCount: int

def main():
  logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
  )

  logging.info("Fetching airport data from %s", AIRPORTS_URL)

  airports_req = requests.get(AIRPORTS_URL)
  if airports_req.status_code != 200:
    logging.error(
      "Request failed with status %s: %s", 
      airports_req.status_code,
      airports_req.text
    )
    raise RuntimeError(f"Failed to fetch airport data from {AIRPORTS_URL} ")
  src_airports = airports_req.json()["airports"]

  routes_req = requests.get(ROUTES_URL)
  if routes_req.status_code != 200:
    logging.error(
      "Request failed with status %s: %s", 
      routes_req.status_code,
      routes_req.text
    )
    raise RuntimeError(f"Failed to fetch routes data from {ROUTES_URL} ")
  src_routes = routes_req.json()["routes"]

  compiled_airports_map: Dict[AirportCode, Airport] = {}
  for airport in src_airports:
    airport_code = airport["iata"]
    compiled_airports_map[airport_code] = {
      "name": airport["name"],
      "municipality": airport["municipality"],
      "city": airport.get("city", None),
      "cityCode": airport.get("cityCode", None),
      "country": airport["country"],
      "region": airport.get("region", None),
      "latitude": airport["latitude"],
      "longitude": airport["longitude"],
      "size": airport["size"],
      "elevationMeters": airport.get("elevationMeters", 0),
      "routeArrivals": [],
      "routeDepartures": []
    }

  compiled_routes_map: Dict[RouteCode, Route] = {}
  for route in src_routes:
    route_code: RouteCode = route["key"]
    departing_airport: AirportCode = route["from"]
    arriving_airport: AirportCode = route["to"]

    route_data: Route = {
      "departureAirport": departing_airport,
      "arrivalAirport": arriving_airport,
      "distanceKm": route["km"],
      "greatCircleKm": route["greatCircleKm"],
      "flightTimeEstimateMin": route["flightTimeEstimateMin"],
      "passengerCount": route["passengers"],
      "seatCount": route["seats"]
    }
    compiled_routes_map[route_code] = route_data

    if departing_airport not in compiled_airports_map:
      raise RuntimeError(f"Departing airport {departing_airport} not found in airports data")
    compiled_airports_map[departing_airport]["routeDepartures"].append(route_code)

    if arriving_airport not in compiled_airports_map:
      raise RuntimeError(f"Arriving airport {arriving_airport} not found in airports data")
    compiled_airports_map[arriving_airport]["routeArrivals"].append(route_code)

  if not os.path.exists(PUBLIC_DATA_PATH):
    os.makedirs(PUBLIC_DATA_PATH)

  with open(COMPILED_AIRPORTS_PATH, "w", encoding="utf-8") as output_file:
    json.dump(compiled_airports_map, output_file, ensure_ascii=False, indent=2)

  with open(COMPILED_ROUTES_PATH, "w", encoding="utf-8") as output_file:
    json.dump(compiled_routes_map, output_file, ensure_ascii=False, indent=2)

  logging.info(
    "Finished processing %d airports and %d routes",
    len(src_airports),
    len(src_routes)
  )
  logging.info("Compiled airport data written to %s", COMPILED_AIRPORTS_PATH)



if __name__ == "__main__":
  main()