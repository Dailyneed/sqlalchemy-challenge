import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to Hawii Climate Analysis API!<br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return last 12 months of precipitation data"""
    # Calculate the date one year from most recent date in database
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Query Mesurement for the last one year date and precpitation
    year_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).all()
    
    session.close()

    # Create a dictionary from the result using date as key and prcp as the value
    all_date_prcp = []
    for date, prcp in year_prcp:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        all_date_prcp.append(measurement_dict)
        
    return jsonify(all_date_prcp)
    
         
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of stations in the dataset"""
    # Query Station for list of stations.
    station_count = session.query(Station.station).all()

    session.close()

    # Convert the result to list
    stations= list(np.ravel(station_count))
    return jsonify(stations)

    
@app.route("/api/v1.0/tobs")
def mostactive_stationtemp():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Calculate the date one year ago from most recent date in database
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the date and temperature of most active station for previous year data
    mostactive_station_tobs= session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= year_ago).all()
    
    session.close()

    # Convert result into list
    active_station_temperatures = list(np.ravel(mostactive_station_tobs))
    return jsonify(active_station_temperatures)

    
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_stat(start=None, end=None):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return minimum, average and maximum temperature"""
    # Create a statement, and use function to find min, avg and max temperature
    tem = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    
    if not end:
    # For a specified start, calculate TMIN, TAVG, and TMAX 
    # for all dates greater than or equal to the start date
        results = session.query(*tem).\
            filter(Measurement.date >= start).all()
        
    # For a specified start date and end date, calculate TMIN, TAVG, and TMAX
    # for the dates from start date to the end date, inclusive.
    else:
        results = session.query(*tem).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
    # Convert results into list
    temp = list(np.ravel(results))
    return jsonify(temp)

          

if __name__ == '__main__':
    app.run(debug=True)

