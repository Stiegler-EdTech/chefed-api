
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()

class Location:
    def __init__(self, latitude, longitude, formatted_address):
        self.latitude = latitude
        self.longitude = longitude
        self.formatted_address = formatted_address

    def get_coordinates(self):
        return self.latitude, self.longitude

    def __repr__(self):
        return f"Location(latitude={self.latitude}, longitude={self.longitude}, formatted_address='{self.formatted_address}')"


def get_location(place) -> Location:
   """   
   Get the latitude and longitude of a place using the Google Maps Geocoding API.
   :param place: The place to geocode. Examples: "1600 Amphitheatre Parkway, Mountain View, CA", "San Francisco, CA", "Paris USA"
   :return: A Location object with the latitude, longitude, and formatted address of the place.
   """

   api_key=os.getenv('GOOGLE_MAPS_API_KEY')
   base_url = "https://maps.googleapis.com/maps/api/geocode/json"

   params = {
      "address": place,
      "key": api_key,
  }

   try:
      response = requests.get(base_url, params=params)
      response.raise_for_status()  # Raise an exception for bad status codes
      data = json.loads(response.text)
      if data["status"] != "OK":
        raise ValueError(f"Geocoding API error: {data['status']}")
      
      location = data["results"][0]["geometry"]["location"]
      formatted_address = data["results"][0]["formatted_address"]
      latitude = location["lat"]
      longitude = location["lng"]
      return Location(latitude, longitude, formatted_address)
   
   except requests.exceptions.RequestException as e:
      print(f"Error during API request: {e}")
      return None


