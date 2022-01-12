//google.charts.load('current', {'packages':['corechart']});
//google.charts.setOnLoadCallback(drawChart);
////google.charts.setOnLoadCallback(drawChart_month);
////google.charts.setOnLoadCallback(drawChart_adm);
//google.charts.setOnLoadCallback(drawChart_1);

function drawChart() {
    var prs_xhr = new XMLHttpRequest();
    var params ='chart'
    prs_xhr.open('GET','?'+params)
    prs_xhr.responseType = 'json';
    prs_xhr.send()
    prs_xhr.onload = function() {
    data = prs_xhr.response
    for (key in data) {
        console.log(key)
        console.log(data[key])
        var data = google.visualization.arrayToDataTable(data[key]);
        var options = {
          title: key,
//          curveType: 'function',
          legend: { position: 'bottom' }
        };
        var chart = new google.visualization.LineChart(document.getElementById('curve_chart'));
        chart.draw(data, options);
    }}

}

function drawChart_adm() {
    var prs_xhr = new XMLHttpRequest();
    var params ='chart_adm'
    console.log('chart_adm')
    prs_xhr.open('GET','?'+params)
    prs_xhr.responseType = 'json';
    prs_xhr.send()
    prs_xhr.onload = function() {
    data = prs_xhr.response
    for (key in data) {
        console.log(key)
        console.log(data[key])
        var data = google.visualization.arrayToDataTable(data[key]);
        var options = {
          title: key,
//          curveType: 'function',
          legend: { position: 'bottom' }
        };
        var chart = new google.visualization.LineChart(document.getElementById('curve_chart_adm'));
        chart.draw(data, options);
    }}

}

function drawChart_1() {
    var prs_xhr = new XMLHttpRequest();
    var params ='chart_depr'
    prs_xhr.open('GET','?'+params)
    prs_xhr.responseType = 'json';
    prs_xhr.send()
    prs_xhr.onload = function() {
    data = prs_xhr.response
    for (key in data) {
        console.log(key)
        console.log(data[key])
        var data = google.visualization.arrayToDataTable(data[key]);
        var options = {
          title: key,
//          curveType: 'function',
          legend: { position: 'bottom' }
        };
        var chart = new google.visualization.LineChart(document.getElementById('curve_chart_depr'));
        chart.draw(data, options);
    }}

}

function drawChart_month() {
    var prs_xhr = new XMLHttpRequest();
    var params ='chart_month'
    prs_xhr.open('GET','?'+params)
    prs_xhr.responseType = 'json';
    prs_xhr.send()
    prs_xhr.onload = function() {
    data = prs_xhr.response
    for (key in data) {
        console.log(key)
        console.log(data[key])
        var data = google.visualization.arrayToDataTable(data[key]);
        var options = {
          title: key,
//          curveType: 'function',
          legend: { position: 'bottom' }
        };
        var chart = new google.visualization.LineChart(document.getElementById('curve_chart_month'));
        chart.draw(data, options);
    }}

}