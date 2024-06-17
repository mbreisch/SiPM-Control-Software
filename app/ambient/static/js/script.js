async function reloadImg(url) {
    try {
        const response = await fetch(url, { cache: 'reload', mode: 'no-cors' });
        if (response.ok) {
            document.body.querySelectorAll(`img[src='${url}']`)
                .forEach(img => img.src = url);
            console.log(`Refreshing image at ${url}`);
        } else {
            console.error(`Failed to load image at ${url}. Retrying...`);
        }
    } catch (error) {
        console.error(`Failed to load image at ${url}. Retrying...`, error);
    }
}

function refreshImage(imageId, imagePath) {
    const img = imagePath;
    reloadImg(img);
}

async function update_cooler() {
    console.log("Updating Cooler Ambients");
    $.ajax("update_cooler", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {
            console.log("Success. Refreshing Image");
            const imageUrl = document.getElementById('Cooler').src;
            refreshImage('Cooler', imageUrl);
        }
    });
}

async function update_darkbox(){
    console.log("Updating Darkbox Ambients");
    $.ajax("update_darkbox", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {
            console.log("Success. Refreshing Image");
            const imageUrl = document.getElementById('Darkbox').src;
            refreshImage('Darkbox', imageUrl);
        }
    });
}

async function update_outside(){
    console.log("Updating Outside Ambients");
    $.ajax("update_outside", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {
            console.log("Success. Refreshing Image");
            const imageUrl = document.getElementById('Outside').src;
            console.log(imageUrl)
            refreshImage('Outside', imageUrl);
        }
    });
}