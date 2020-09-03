const puppeteer = require('puppeteer');
var filename =  "temp/"+process.argv[2];
var day = +process.argv[3];
var url =  "http://127.0.0.1:8081/chart?day="+day;
if(day > 180){
	  day=180
}

(async () => {

  var browser = await puppeteer.launch({
	 headless: true,
  });
const page = await browser.newPage();
try{await page.goto(url, {"waitUntil" : "networkidle2"});  }catch(err){await browser.close();}
const header = await page.$('html');

  var doc = await page.evaluate((header) => {
    const {x, y, width, height} = header.getBoundingClientRect();
    return {x, y, width, height};
  }, header);

	  w=day * 35
	  if(w<500) w = 500;
  
await page.setViewport({ width: Math.round(w) , height: Math.round(doc.height)});
await page.waitFor(2000);
 await page.screenshot({path: filename,quality: 90});
  await browser.close();
})();