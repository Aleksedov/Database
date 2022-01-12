var ctxs = document.getElementsByTagName('canvas');

for (i in ctxs){
 make_chart(ctxs[i])
}

function make_chart(cns){
    var ctx = cns.getContext('2d');
    var get_key = cns.id;
    var prs_xhr = new XMLHttpRequest();
    prs_xhr.open('GET','?'+get_key)
    prs_xhr.responseType = 'json';
    prs_xhr.send()
    prs_xhr.onload = function() {
    var data = prs_xhr.response
    console.log(data)
    for (i in data["datasets"]){
    data["datasets"][i]["fill"] = false
    data["datasets"][i]["tension"] = 0.1
    console.log(data["datasets"][i])}
    var myChart = new Chart(ctx, {

        "type": "line",
        "data": data,
        "options": {}
        });
}}

