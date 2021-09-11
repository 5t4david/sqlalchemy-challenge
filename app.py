import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Base.metadata.tables # Check tables, not much useful
# Base.classes.keys() # Get the table names

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
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    queryresult = session.query(*sel).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    queryresult = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()

    stations = []
    for station,name,lat,lon,el in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    last_data_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_data_date_dt = dt.datetime.strptime(last_data_date, '%Y-%m-%d')
    one_year_ago = dt.date(last_data_date_dt.year -1, last_data_date_dt.month, last_data_date_dt.day)
    queryresult = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= one_year_ago).all()
    session.close()

    tobs_data = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route('/api/v1.0/<start>')
def get_t_start(start):
    session = Session(engine)
    queryresult = (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).
        filter(Measurement.date >= start).all()
    )
    session.close()

    tobs_data = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

@app.route('/api/v1.0/<start>/<stop>')
def get_t_start_stop(start,stop):
    session = Session(engine)
    queryresult = (session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).
        filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    )
    session.close()

    tobs_data = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)

if __name__ == '__main__':
    app.run(debug=True)