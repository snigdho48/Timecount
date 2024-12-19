from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app) 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'snigdho'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Snigdho48.'
app.config['MYSQL_DATABASE_DB'] = 'kamasutra'
app.config['MYSQL_DATABASE_HOST'] = '128.199.157.215'

mysql = MySQL()
mysql.init_app(app)

def create_table():
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        create_query = """
        CREATE TABLE IF NOT EXISTS reportdata (
            id INT AUTO_INCREMENT PRIMARY KEY,
            ip VARCHAR(15) NOT NULL,
            portalID INT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            count INT NOT NULL
        )
        """
        cursor.execute(create_query)
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

# Helper function to insert data into the database
def input_data(ip, portalID, timestamp, count=0):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO reportdata (ip, portalID, timestamp, count)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (ip, portalID, timestamp, count))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error inserting data: {e}")
        return False
    return True

# Helper function to update data in the database
def update_data(id, timestamp, count):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        update_query = """
        UPDATE reportdata
        SET count = %s, timestamp = %s
        WHERE id = %s
        """
        cursor.execute(update_query, (count, timestamp, id))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error updating data: {e}")
        return False
    return True

@app.route('/api/kamasutra', methods=['POST'])
def post_data():
    try:
        if 'ip' not in request.json or 'portalID' not in request.json and 'closed' not in request.json:
            return jsonify({"error": "Missing required fields: 'ip' and 'portalID'"}), 400

        ip = request.json['ip']
        portalID = request.json['portalID']
        closed = request.json['closed']
        
        if not isinstance(ip, str) or not isinstance(portalID, int) or len(ip) > 15 or portalID < 0 or portalID > 65535 and not isinstance(closed, bool):
            return jsonify({"error": "Invalid data types"}), 400
        
        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT * FROM reportdata WHERE ip=%s AND portalID=%s"
        cursor.execute(query, (ip, portalID))
        rows = cursor.fetchall()
        timestamp = datetime.datetime.now()
        timediff = 0
        difference=0
        id = rows[0][0] if len(rows) > 0 else None
        
        if len(rows) == 0:
            if not input_data(ip, portalID, timestamp,1):
                return jsonify({"error": "Failed to insert data into database"}), 400
        else:
            timediff = timestamp - rows[0][3]  
            difference=timediff.total_seconds()
            difference= round(difference/60,2)
            if not update_data(id, timestamp, rows[0][4] + 1):  
                return jsonify({"error": "Failed to update data in database"}), 400

        cursor.close()
        conn.close()
     
        if closed:
            return jsonify({"received": 'Success', 'time': '0'}), 201
        return jsonify({"received": 'Success', 'time': str(difference)}), 201

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    create_table()
    app.run(debug=True)
    

