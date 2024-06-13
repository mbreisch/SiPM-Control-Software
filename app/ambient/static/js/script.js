let tempIntervalId = null;
let adcIntervalId = null;

async function get_temp_values() {
    console.log("Refreshing \x1b[32mTemperature\x1b[0m \x1b[35mValues\x1b[0m at: " + new Date().toLocaleTimeString());
    $.ajax("get_temp_values", {
        contentType: "application/json",
        data: JSON.stringify({ variable: "temperature values" }),
        type: "POST",
        success: function(response) {
            var data = response.data;
            console.log(data["temps"]);
            console.log("\x1b[32mTemperature\x1b[0m Read \x1b[31mException\x1b[0m = " + data["Exception"]);
            for (let idx = 0; idx < data["temps"].length; idx++) {
                var row = Math.floor(idx);
                if (data["temps"][idx] != 0) {
                    document.getElementById(`label${row}`).innerHTML = data["temps"][idx];
                    if(data["temps"][idx]>=30){
                        document.getElementById(`label${row}`).style.color = "rgb(215, 102, 12)";
                    }else if(data["temps"][idx]>=25 && data["temps"][idx]<30){
                        document.getElementById(`label${row}`).style.color = "rgb(0, 255, 0)";
                    }else if(data["temps"][idx]<25){
                        document.getElementById(`label${row}`).style.color = "rgb(13, 152, 213)";
                    }else{
                        document.getElementById(`label${row}`).style.color = "rgb(0, 255, 0)";
                    }
                } else {
                    document.getElementById(`label${row}`).style.color = "rgb(0, 255, 0)";
                    document.getElementById(`label${row}`).innerHTML = `${row}`;
                }
            }
        }
    });
}

function startTempInterval() {
    if (tempIntervalId === null) {
        get_temp_values(); // Run once immediately
        tempIntervalId = setInterval(get_temp_values, 10000);
    } else {
        get_temp_values(); // Run once if already running
    }
}

async function reloadImg(url) {
    await fetch(url, { cache: 'reload', mode: 'no-cors' });
    document.body.querySelectorAll(`img[src='${url}']`)
      .forEach(img => img.src = url);
  }

async function init_temp_func() {
    console.log("Initialising Temperature Sensors");
    $.ajax("init_temperature", {
        contentType: "application/json",
        data: JSON.stringify({ variable: "init_temperature" }),
        type: "POST",
        success: function(response) {
            var data = response.data;
            console.log(data);
            for (let idx = 0; idx < data.length; idx++) {
                var row = Math.floor(idx);
                if (data[idx] != 0) {
                    document.getElementById(`label${row}`).style.color = "rgb(0, 255, 0)";
                } else {
                    document.getElementById(`label${row}`).style.color = "rgb(255, 0, 0)";
                }
            }
        }
    });
}

async function get_adc_values() {
    console.log("Refreshing \x1b[33mVoltage\x1b[0m \x1b[35mValues\x1b[0m at: " + new Date().toLocaleTimeString());
    $.ajax("get_adc_value", {
        contentType: "application/json",
        data: JSON.stringify({ voltage_card: 0 }),
        type: "POST",
        success: function(response) {
            var data = response.data;
            if (data && data["voltages"]) {
                console.log("\x1b[33mVoltage\x1b[0m Read \x1b[31mException\x1b[0m = " + data["Exception"]);
                var arraylength = data["voltages"].length;
                try {
                    for (let chan = 0; chan < arraylength; chan++) {
                        document.getElementById(`ADCVal${chan}`).value = data["voltages"][chan];
                    }
                } catch (e) {
                    console.log(e.name + ': ' + e.message);
                }
            }
        }
    });
}

function startAdcInterval() {
    if (adcIntervalId === null) {
        get_adc_values(); // Run once immediately
        adcIntervalId = setInterval(get_adc_values, 30000);
    } else {
        get_adc_values(); // Run once if already running
    }
}

function set_dac_value(val, chan, slider_val) {
    val = document.getElementById(`involt${chan}`).value;
    console.log(`Set Bias Voltage of ${chan} to ${val}`);
    $.ajax("set_dac_value", {
        contentType: "application/json",
        data: JSON.stringify({ voltage: val, channel: chan }),
        type: "POST",
        success: function(response) {
            var data = response.data;
            console.log("\x1b[33mVoltage\x1b[0m Write \x1b[31mException\x1b[0m = " + data["Exception"]);
            document.getElementById(`involt${chan}`).value = data["voltage"];
            document.getElementById(`ADCVal${chan}`).value = data["adc_voltage"];
        }
    });
}

function init_dac_func() {
    console.log("Initialising ADC/DACs");
    $.ajax("init_dac", {
        contentType: "application/json",
        data: JSON.stringify({ variable: "init_dac" }),
        type: "POST",
        success: function(response) {
            var data = response.data;
            console.log(data);
        }
    });
}

function set_all_value(slider_val) {
    let val = document.getElementById(`involt_all`).value;
    console.log(`set all dac value ${val}`);
    for (let chan = 0; chan < 8; chan++) {
        $.ajax("set_dac_value", {
            contentType: "application/json",
            data: JSON.stringify({ voltage: val, channel: chan }),
            type: "POST",
            success: function(response) {
                var data = response.data;
                console.log(data["Exception"]);
                document.getElementById(`involt${chan}`).value = data["voltage"];
                document.getElementById(`ADCVal${chan}`).value = data["adc_voltage"];
                document.getElementById(slider_val).innerHTML = data["voltage"];
            }
        });
        sleep(10000);
    }
}

function sleep(milliseconds) {
    const date = Date.now();
    let currentDate = null;
    do {
        currentDate = Date.now();
    } while (currentDate - date < milliseconds);
}


function hello_world(){
    console.log("Hello World")
}