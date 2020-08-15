from module.wikiPic import *
from flask import Flask, request
from module.dateParse import *
import json
app = Flask (__name__)

@app.route('/')
def hello() -> str:
    args = request.args
    wikiPicDate:str
    if "date" in args:
        wikiPicDate = args["date"]
    else:
        DateTimeGenerator_obj = DateTimeGenerator()
        wikiPicDate = datetime.strptime(DateTimeGenerator_obj.timestampToDateTime(), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
    wikiPic_obj = WikiPic()
    wikiPicJson = wikiPic_obj.getWikiPic(wikiPicDate)
    print(json.dumps(wikiPicJson))
    return str(wikiPicJson)

app.run(debug=True)
