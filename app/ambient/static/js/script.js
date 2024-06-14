async function reloadImg(url) {
    await fetch(url, { cache: 'reload', mode: 'no-cors' });
    document.body.querySelectorAll(`img[src='${url}']`)
      .forEach(img => img.src = url);
}

function refreshImage(imageId, imagePath) {
    const img = imagePath;
    reloadImg(img)
    .then(() => {
        console.log(`Refreshing image ${imageId} at: ` + new Date().toLocaleTimeString());
    })
    .catch(error => {
        console.error(`Failed to load image ${imageId}. Retrying...`, error);
    });
}

async function update_cooler(){
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
            refreshImage('Outside', imageUrl);
        }
    });
}