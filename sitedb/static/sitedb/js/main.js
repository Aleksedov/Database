const sw = document.getElementById('customSwitch1'); // переключатель лишенных свободы
const sw2 = document.getElementById('customSwitch2'); // переключатель мест лишения свободы
const sw3 = document.getElementById('customSwitch3'); // переключатель мест лишения свободы с политЗК
var swLabel = document.querySelector('.custom-control-label');
var swLabel2 = document.getElementsByName('ap_label');
var form = document.querySelector('#filter-form');

//фильтр элементов по строке поиска
function input_Func() {
    input = document.querySelector("#search-field").value.toUpperCase();
    console.log(input)
    if (event.keyCode == '13'){
        var form = document.querySelector('form')
        form.submit()
    }}


function show_prisoned() {
    swLabel.textContent = (swLabel.textContent === 'Показать лишенных свободы') ? 'Показать всех':'Показать лишенных свободы';
    form.submit()
    }
if (sw) {sw.addEventListener('click', show_prisoned)}


function show_prison() {
    swLabel.textContent = (swLabel.textContent === 'Места лишения свободы') ? 'Показать всех':'Места лишения свободы';
    form.submit()
    }
if (sw2) {sw2.addEventListener('click', show_prison)}

function show_prison_curr() {
    swLabel2.textContent = (swLabel.textContent === 'С политЗК') ? 'Все':'С политЗК';
    form.submit()
    }
if (sw3) {sw3.addEventListener('click', show_prison_curr)}

//Поиск элементов в выпадащем списке фильтрации
function fil_Func(key) {
    console.log(key)
    div = document.getElementById(key);
    input = div.querySelector("#myInput");
    filter = input.value.toUpperCase();
    li = div.getElementsByTagName("li");
     for (i = 0; i < li.length; i++) {
        txtValue = li[i].textContent || li[i].innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
              li[i].style.display = "";
            } else {
              li[i].style.display = "none";
            }
        }
     }

//формирует список виновных в преследовании на основании JS запроса
function take_items_list(key) {
    console.log(key)
    div_m = document.getElementById(key);
    var prs_xhr = new XMLHttpRequest();
    var params ='prs='+key
    prs_xhr.open('GET','?'+params)
    prs_xhr.responseType = 'json';
    prs_xhr.send()
    prs_xhr.onload = function() {
    data = prs_xhr.response
    console.log(data)
    var old_ul = div_m.querySelector("ul");
    old_ul.parentNode.removeChild(old_ul);
    var new_ul = document.createElement("ul");
    new_ul.class = "item_list"
    console.log(new_ul)
    div_m.appendChild(new_ul)
    for (glty in data) {
    new_li = document.createElement("li");
    new_ul.appendChild(new_li)
    new_a = document.createElement("a");
    new_a.href = '/persons/'+glty
    new_a.innerText = data[glty]
    new_li.appendChild(new_a)
        }
    }
    }
