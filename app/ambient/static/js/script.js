async function reloadImg(url) {
    try {
        const response = await fetch(url, { cache: 'reload' });
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

async function refreshImage(imagePath) {
    const img = new URL(imagePath, window.location.href).href;
    await reloadImg(img);
}

async function update_cooler() {
    console.log("Updating Cooler Ambients");
    $.ajax("update_cooler", {
        contentType: "application/json",
        type: "POST",
        success: async function(response) {
            console.log("Success. Refreshing Image");
            const imageUrl = document.getElementById('Cooler').src;
            await refreshImage(imageUrl);
        }
    });
}

async function update_darkbox(){
    console.log("Updating Darkbox Ambients");
    $.ajax("update_darkbox", {
        contentType: "application/json",
        type: "POST",
        success: async function(response) {
            console.log("Success. Refreshing Image");
            const imageUrl = document.getElementById('Darkbox').src;
            await refreshImage(imageUrl);
        }
    });
}

async function update_outside(){
    console.log("Updating Outside Ambients");
    $.ajax("update_outside", {
        contentType: "application/json",
        type: "POST",
        success: async function(response) {
            console.log("Success. Refreshing Image");
            const imageUrl = document.getElementById('Outside').src;
            await refreshImage(imageUrl);
        }
    });
}
