async function reloadImg(name, url) {
    console.log(`Reloading ${name} at ${url}`);
    try {
        const timestamp = Date.now(); // Unique timestamp for each image fetch
        const uniqueUrl = `${url}?timestamp=${timestamp}`;
        
        const response = await fetch(uniqueUrl);
        if (response.ok) {
            // Update all images with the same src URL
            document.body.querySelectorAll(`img[src='${url}']`)
                .forEach(img => img.src = uniqueUrl);
        } else {
            console.error(`Failed to load image at ${url}. Retrying...`);
        }
    } catch (error) {
        console.error(`Failed to load image at ${url}. Retrying...`, error);
    }
}

function update_cooler() {
    console.log("Updating Cooler Ambients");
    $.ajax("update_cooler", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {
            const imageUrl = document.getElementById('Cooler').src;
            reloadImg('Cooler', imageUrl);
        }
    });
}

function update_darkbox(){
    console.log("Updating Darkbox Ambients");
    $.ajax("update_darkbox", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {
            const imageUrl = document.getElementById('Darkbox').src;
            reloadImg('Darkbox', imageUrl);
        }
    });
}

function update_outside(){
    console.log("Updating Outside Ambients");
    $.ajax("update_outside", {
        contentType: "application/json",
        type: "POST",
        success: function(response) {
            const imageUrl = document.getElementById('Outside').src;
            reloadImg('Outside', imageUrl);
        }
    });
}
