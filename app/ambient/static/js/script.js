async function reloadImg(url) {
    await fetch(url, { cache: 'reload', mode: 'no-cors' });
    document.body.querySelectorAll(`img[src='${url}']`)
      .forEach(img => img.src = url);
}

async function update_cooler() {
    console.log("Updating Cooler Ambients");
    $.ajax("update_cooler", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {}
    });
}

async function update_darkbox(){
    console.log("Updating Darkbox Ambients");
    $.ajax("update_darkbox", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {} 
    });
}

async function update_outside(){
    console.log("Updating Outside Ambients");
    $.ajax("update_outside", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {} 
    });
}

async function fetchFanStatus() {
    try {
        const response = await fetch('http://templogpi.am14.uni-tuebingen.de:5000/fan_status');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        document.getElementById('countdown').textContent = data.countdown;
        document.getElementById('relay').textContent = data.relay;
    } catch (error) {
        console.error('Fetch error:', error);
        document.getElementById('countdown').textContent = 'Error';
        document.getElementById('relay').textContent = 'Error';
    }
}

async function sendFanControl() {
    let modeToggle = document.getElementById('modeToggle');
    let offTime = -1;
    let onTime = -1;
    let autoToggle = -1;
    if(modeToggle.checked) { //Manual mode
        offTime = document.getElementById('offTime').value;
        onTime = document.getElementById('onTime').value;
    }else if(!modeToggle.checked){ //Auto mode
        autoToggle = document.getElementById('autoToggle').checked;
    }
    try {
        const response = await fetch('http://raspberrypisipm.am14.uni-tuebingen.de:5000/ambient/fan_control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mode: modeToggle.checked, offTime: offTime, onTime: onTime, autoToggle: autoToggle}),
        });
        // Check if response is okay
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('Success:', data);
        } catch (error) {
            console.error('Fetch Error:', error);
        }
}

async function fetchRHTStatus() {
    try {
        const response = await fetch('http://templogpi.am14.uni-tuebingen.de:5000/rht_status');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        console.log("Got json data:", data);

        $.ajax("save_rht", {
            contentType: "application/json",
            data: JSON.stringify({ cooler: data.cooler, darkbox: data.darkbox, outside: data.outside}),
            type: "POST",
            success: function(response) {}
        });
        
    } catch (error) {
        console.error('Fetch error:', error);
    }
}

async function set_plot_settings(name, subname, id, value){
    $.ajax("set_plot_settings", {
        contentType: "application/json",
        data: JSON.stringify({ name: name, subname: subname, id: id, value: value}),
        type: "POST",
        success: function(response) {
            console.log("Got json data:", name, subname, id, value, response);
            // Update LED indicators based on the response
            if (id === 0) { // Set mode
                document.getElementById(`led-${subname}`).classList.add('on');
                document.getElementById(`led-${subname}-auto`).classList.remove('on');
            } else if (id === -1) { // Auto mode
                document.getElementById(`led-${subname}`).classList.remove('on');
                document.getElementById(`led-${subname}-auto`).classList.add('on');
            }
            saveSettingToLocalStorage(name, subname, id, value);
        },
        error: function(xhr, status, error) {
            console.error("Error setting plot settings: ", status, error);
        }
    });
}


function saveSettingToLocalStorage(name, subname, id, value) {
    const settings = JSON.parse(localStorage.getItem('settings')) || [];
    const settingIndex = settings.findIndex(setting => setting.subname === subname);

    if (settingIndex >= 0) {
        settings[settingIndex] = { name, subname, id, value };
    } else {
        settings.push({ name, subname, id, value });
    }

    localStorage.setItem('settings', JSON.stringify(settings));
}

function applySavedSettings() {
    const settings = JSON.parse(localStorage.getItem('settings')) || [];

    settings.forEach(setting => {
        set_plot_settings(setting.name, setting.subname, setting.id, setting.value);
    });
}