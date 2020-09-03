var json_src=null;
var defer = $.Deferred();
var t={};
let download_port = []; 
let download_list=new Array();
var _r = function (){

    $.ajax({
        // async:false,
        url : 'http://127.0.0.1:8081/api/ccsun?day='+ GetQueryString("day"),

        beforeSend: function(){
            console.log("loading...");

        },
        success : function(result){
            // json_src = result;
            //   create_img();
            defer.resolve(result);
        }
    });
    return defer.promise();
};

$.when(_r()).done(function(result){
    json_src =  JSON.parse(result);
    loaded();

});

function loaded(){
var chart1=  Highcharts.chart('container', {
    chart: {
        type: 'line'
    },
	credits: { enabled: false } ,
    title: {
        text: '当日流量'
    },
    subtitle: {
        text: ''
    },
    xAxis: {
       
    },
    yAxis: {
        title: {
            text: '流量 (GB)'
        }
    },
    plotOptions: {
        line: {
            dataLabels: {
                enabled: true
            },
            enableMouseTracking: false
        }
    },
    series: []
});
let date =[];
let download = [];
let upload = [];
for(let i=0 ;i < json_src["data"].length;i++){
	
	date.push(json_src["data"][i]["date"]);
 chart1.xAxis[0].setCategories(date);
 download.push(parseFloat(json_src["data"][i]["download"]));
  upload.push(parseFloat(json_src["data"][i]["upload"]));
 
	 
}
 var d = {
       name: '下载',
        data: download
    };

 chart1.addSeries(d);
  var d = {
       name: '上传',
        data: upload
    };

 chart1.addSeries(d);
 
 //2
 
var chart2=  Highcharts.chart('container2', {
    chart: {
        type: 'line'
    },
	credits: { enabled: false } ,
    title: {
        text: '总计流量'
    },
    subtitle: {
        text: ''
    },
    xAxis: {
       
    },
    yAxis: {
        title: {
            text: '流量 (GB)'
        }
    },
    plotOptions: {
        line: {
            dataLabels: {
                enabled: true
            },
            enableMouseTracking: false
        }
    },
    series: []
});
 
 
 date =[];
 download = [];
 upload = [];
for(let i=0 ;i < json_src["data"].length;i++){
	
	date.push(json_src["data"][i]["date"]);
 chart2.xAxis[0].setCategories(date);

 download.push(parseFloat(json_src["data"][i]["used"]["download"]));
  upload.push(parseFloat(json_src["data"][i]["used"]["upload"]));
 
	 
}

 var d = {
       name: '下载',
        data: download
    };

 chart2.addSeries(d);
  var d = {
       name: '上传',
        data: upload
    };

 chart2.addSeries(d);




}

    function GetQueryString(name) { 
      var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i"); 
      var r = window.location.search.substr(1).match(reg); //获取url中"?"符后的字符串并正则匹配
      var context = ""; 
      if (r != null) 
         context = r[2]; 
      reg = null; 
      r = null; 
      return context == null || context == "" || context == "undefined" ? "" : context; 
    }