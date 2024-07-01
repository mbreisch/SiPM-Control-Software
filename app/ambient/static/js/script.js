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

async function fetchStatus() {
    try {
        const response = await fetch('http://templogpi.am14.uni-tuebingen.de:5000/status');
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

async function set_plot_settings(name, subname, id){
    let value;
    if (id == -1){
        value = -1;
    }else{
        value = document.getElementById(subname).value;
    }

    $.ajax("set_plot_settings", {
        contentType: "application/json",
        data: JSON.stringify({ name: name, subname: subname, value: value, id: id}),
        type: "POST",
        success: function(response) {
            // Update LED indicators based on the response
            if (id === 0) { // Set mode
                document.getElementById(`led-${subname}`).classList.add('on');
                document.getElementById(`led-${subname}-auto`).classList.remove('on');
            } else if (id === -1) { // Auto mode
                document.getElementById(`led-${subname}`).classList.remove('on');
                document.getElementById(`led-${subname}-auto`).classList.add('on');
            }
            saveSettingToLocalStorage(name, subname, value, id);
        },
        error: function(xhr, status, error) {
            console.error("Error setting plot settings: ", status, error);
        }
    });
}


function saveSettingToLocalStorage(name, subname, value, id) {
    const settings = JSON.parse(localStorage.getItem('settings')) || [];
    const settingIndex = settings.findIndex(setting => setting.subname === subname);

    if (settingIndex >= 0) {
        settings[settingIndex] = { name, subname, value, id };
    } else {
        settings.push({ name, subname, value, id });
    }

    localStorage.setItem('settings', JSON.stringify(settings));
}

function applySavedSettings() {
    const settings = JSON.parse(localStorage.getItem('settings')) || [];

    settings.forEach(setting => {
        set_plot_settings(setting.name, setting.subname, setting.value);
    });
}