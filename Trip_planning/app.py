# Import the dependencies.

#################################################
# Database Setup
#################################################
# reflect an existing database into a new model
# reflect the tables
# Save references to each table
# Create our session (link) from Python to the DB
#################################################
# Flask Setup
#################################################
#################################################
# Flask Routes
#################################################

# Import necessary libraries
import datetime as dt
import numpy as np
import pandas as pd
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Set up the Flask app
app = Flask(__name__)

# Create the engine and reflect the database
database_path = "../Resources/hawaii.sqlite"
engine = create_engine(f"sqlite:///{database_path}")
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Home route to list all available routes
@app.route("/")
def home():
    return (
        "Welcome to the Hawaii Climate API<br/>"
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

# Precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    latest_date = session.query(func.max(Measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)
    
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
                         filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

# Stations route
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stations_data = session.query(Station.station).all()
    session.close()
    
    stations_list = list(np.ravel(stations_data))
    return jsonify(stations_list)

# Temperature Observations route
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = session.query(Measurement.station).\
                          group_by(Measurement.station).\
                          order_by(func.count(Measurement.station).desc()).first()[0]

    latest_date = session.query(func.max(Measurement.date)).filter(Measurement.station == most_active_station).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    one_year_ago = latest_date - dt.timedelta(days=365)
    
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
                       filter(Measurement.station == most_active_station).\
                       filter(Measurement.date >= one_year_ago).all()
    
    session.close()
    
    temperature_list = [temp for date, temp in temperature_data]
    return jsonify(temperature_list)

# Start and End Date route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end=None):
    session = Session(engine)
    
    if end:
        temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()
    
        print("Received start:", start)
        print("Received end:", end)

        if end:
            print("Query with end date:", session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start).filter(Measurement.date <= end))
        else:
            print("Query without end date:", session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                                filter(Measurement.date >= start))

    session.close()
    
    temperature_stats_list = [{"TMIN": tmin, "TAVG": tavg, "TMAX": tmax} for tmin, tavg, tmax in temperature_stats]
    return jsonify(temperature_stats_list)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
