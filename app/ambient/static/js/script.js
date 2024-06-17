async function reloadImg(url) {
    try {
        // Fetch the image to ensure it's reloaded
        await fetch(url, { cache: 'reload', mode: 'no-cors' });

        // Update all images with matching src attribute
        document.body.querySelectorAll(`img[src='${url}']`).forEach(img => {
            img.src = url + `?timestamp=${new Date().getTime()}`;
        });

        console.log(`Image reloaded: ${url}`);
    } catch (error) {
        console.error(`Failed to reload image: ${url}`, error);
        // Handle error as needed, e.g., retry, log, or display a message
    }
}

function refreshCooler() {
    const imgUrl = "{{ url_for('ambient.static', filename='Ambient_cooler.png') }}";
    reloadImg(imgUrl);
}

function refreshDarkbox() {
    const imgUrl = "{{ url_for('ambient.static', filename='Ambient_darkbox.png') }}";
    reloadImg(imgUrl);
}

function refreshOutside() {
    const imgUrl = "{{ url_for('ambient.static', filename='Ambient_outside.png') }}";
    reloadImg(imgUrl);
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
