import sqlite3
import sys
sys.path.append('..')
from module.wikiPic import *
from flask import Flask, request, render_template, url_for
from module.dateParse import *
import json
from flask_cors import *
app = Flask (__name__)
CORS(app, resources=r'/*')

@app.route('/api/wikipic')
def _wikipicAPI():
    args = request.args
    wikiPicDate:str
    if "date" in args:
        wikiPicDate = args["date"]
    else:
        DateTimeGenerator_obj = DateTimeGenerator()
        wikiPicDate = datetime.strptime(DateTimeGenerator_obj.timestampToDateTime(), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    wikiPic_obj = WikiPic("../config/config.json")
    wikiPicJson = wikiPic_obj.getWikiPic(wikiPicDate)
    print(json.dumps(wikiPicJson))
    return str(wikiPicJson)

@app.route('/api/ccsun')
def _ccsunAPI():
    args = request.args
    if 'day' in args:
        day = args["day"]
        if day == "":day = "7"
    else:
        day = "7"
    path = "../ccsun/"
    conn = sqlite3.connect(f'{path}ccsun.db')
    cur = conn.cursor()
    result =list(cur.execute( "SELECT * FROM ccsun WHERE date >= (SELECT DATETIME('now', '-" + str(int(day) + 1) + " day'))"))
    conn.commit()
    conn.close()

    jsonObj = {
        "data":[],
        "status": "ok",
    }
    if len(result) > 0:
        for x in result:
            id = x[0]
            date = x[1]
            upload = x[2]
            download = x[3]
            uploaded = x[4]
            downloaded = x[5]
            jsonObj["data"].append({
                "date": date,
                "upload":upload,
                "download": download,
                "used":{
                    "upload": uploaded,
                    "download": downloaded
                }
            })
    else:
        jsonObj["status"] = "void"

    return json.dumps(jsonObj)

@app.route('/chart')
def _chart() -> str:
    url_for('static', filename='js/ccsun.js')
    url_for('static', filename='js/highcharts.js')
    url_for('static', filename='js/jquery-1.7.1.min.js')
    return render_template('chart.htm')

app.run(debug=True,port= 8081)
