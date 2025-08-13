#file that will contain all the tools the agent needs such as: 
# Database, Looking up a specific user info, creating a new user, shceedule a meeting, etc.

from livekit.agents import llm
import enum 
from typing import Annotated
import logging
from db_driver import DatabaseDriver

logger = logging.getLogger("user-data")
logger.setLevel(logging.INFO) 

DB = DatabaseDriver() # Initialize the database driver

class CarDetails(enum.Enum): 
    vin = "vin"
    make = "make"
    model = "model"
    year = "year"

class AssistantFnc(llm.FunctionContext): # Function context for the assistant to handle car-related operations
    def __init__(self):
        super().__init__()

        self._car_detail = {  # Initialize car details with empty values
            CarDetails.vin: "",
            CarDetails.make: "",
            CarDetails.model: "",   
            CarDetails.year: ""
        }
    def get_car_string(self): 
        car_str = ""
        for key, value in self._car_.item(): 
            car_str += f"{key}: {value}\n"

        return car_str

    @llm.ai_callable(description="Look up a car by VIN ")
    def lookup_car(self, vin: Annotated[str, llm.TypeInfo(description="VIN of the car to look up")]): # Look up a car by its VIN
        logger.info("look up car - vin: %s", vin) # Log the VIN being looked up

        result = DB.get_car_by_vin(vin) # Retrieve the car by VIN from the database
        if result is None: 
            return "car not found"
        self._car_detail = { # Update the car details with the retrieved car information
            CarDetails.vin: result.vin,
            CarDetails.make: result.make,
            CarDetails.model: result.model,
            CarDetails.year: result.year
        }

        car_str = ""
        for key, value in self._car_.item(): 
            car_str += f"{key}: {value}\n"

        return f"Car details: \n{self.get_car_string()}"
    
    @llm.ai_callable(description="Create a new car record")
    def create_car(self,
                    vin: Annotated[str, llm.TypeInfo(description="Create a new car to add to the database")],
                    make: Annotated[str, llm.TypeInfo(description="Make of the car to add to the database")],
                    model: Annotated[str, llm.TypeInfo(description="Model of the car to add to the database")],
                    year: Annotated[int, llm.TypeInfo(description="Year of the car to add to the database")]
                    ): # create a new car record in the database
        
        logger.info("create car - vin: %s, make: %s, model: %s, year: %d", vin, make, model, year) # Log the car details being created
        result = DB.create_car(vin, make, model, year)
        if result is None:
            return "Failed to create new car"
        
        self._car_detail = { # Update the car details with the newly created car
            CarDetails.vin: result.vin,
            CarDetails.make: result.make,
            CarDetails.model: result.model,
            CarDetails.year: result.year
        }

        return "Car Created"
    
    def has_car(self): # Check if the car details are available
        return self._car_detail[CarDetails.vin] !=""
    
    @llm.ai_callable(description="Get the Details of the car you are currently working with") # Get the details of the car currently being worked with
    def get_car_details(self): 
        logger.info("get car details")
        return f"Car details are: {self.get_car_string()}" if self.has_car() else "No car Details available" #return the car details if available, otherwise return a message indicating no details are available