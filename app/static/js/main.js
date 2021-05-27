function get_prediction() {
    values = [document.getElementById("1").value, document.getElementById("2").value,
    document.getElementById("3").value, document.getElementById("4").value,
    document.getElementById("5").value, document.getElementById("6").value,
    document.getElementById("7").value, document.getElementById("8").value];

    $.ajax({
        url: '/predict',
        type: 'get',
        data: {values: values.join(",")},
        success(data) {
            document.getElementById("result-value").innerHTML = data.data;
        }
    });
}


