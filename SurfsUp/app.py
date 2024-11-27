# Import the dependencies.
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime

#################################################
# Database Setup
#################################################

# Create an engine to connect to the database
engine = create_engine('sqlite:///Resources/hawaii.sqlite') 

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement


#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return(
        f"Welcome to Hawaii Climate API!<br/>"
        f"-----------------------------------<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Retrieve the last 12 months of data
    latest_date_str = session.query(func.max(measurement.date)).scalar()
    latest_date = datetime.datetime.strptime(latest_date_str, '%Y-%m-%d')
    last_twelve = latest_date - datetime.timedelta(days=365)

    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= last_twelve).all()
    session.close()

    # Convert to a dictionary
    precipitation_dict = {date: prcp for date, prcp in results}

    # Return the JSON representation
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB    
    session = Session(engine)
    results = session.query(station.station).all()

    session.close()

    # Convert to a list
    station_list = [station[0] for station in results]
    
    # Return the JSON representation
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Most-active station
    most_active = 'USC00519281'

    # Retrieve the last 12 months of data
    latest_date_str = session.query(func.max(measurement.date)).scalar()
    latest_date = datetime.datetime.strptime(latest_date_str, '%Y-%m-%d')
    last_twelve = latest_date - datetime.timedelta(days=365)

    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active, 
                                                                       measurement.date >= last_twelve).all()
    
    session.close()

    # Convert into a list/dictionary
    temp_data = [{"date": date, "tobs": tobs} for date, tobs in results]
    
    # Return the JSON representation
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def start_date(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    try:
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Calculate TMIN, TAVG, and TMAX from the specified date
    results = session.query(func.min(measurement.tobs), 
                            func.avg(measurement.tobs), 
                            func.max(measurement.tobs)).filter(measurement.date >= start_date).all()
    
    session.close()

    # Check if results are available
    if results[0][0] is None:
        return jsonify({"error": f"No data available from {start}"}), 404

    # Convert the result into a dictionary
    start_data = {"Start Date": start,
                  "TMIN": results[0][0],
                  "TAVG": results[0][1],
                  "TMAX": results[0][2]
    }

    # Return the JSON representation
    return jsonify(start_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_dates(start,end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    try:
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error":"Invalid date format. Use YYYY-MM-DD."}), 400

   # Calculate TMIN, TAVG, and TMAX from the specified date
    results = session.query(func.min(measurement.tobs), 
                            func.avg(measurement.tobs), 
                            func.max(measurement.tobs)).filter(measurement.date >= start_date, 
                                                               measurement.date <= end_date).all()
    
    session.close()    

    # Check if results are available
    if results[0][0] is None:
        return jsonify({"error": f"No data available from {start} to {end}"}), 404

    # Convert the result into a dictionary
    data_range_data = {"Start Date": start, 
                       "End Date": end, 
                       "TMIN": results[0][0],
                       "TAVG": results[0][1],
                       "TMAX": results[0][2]
    }

    # Return the JSON representation
    return jsonify(data_range_data)

if __name__ == "__main__":
    app.run(debug=True)