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

function set_plot_amount(){
    var amount = document.getElementById("plot_amount").value;
    var ylimit_ax1_min = document.getElementById("ylimit_ax1_min").value;
    var ylimit_ax1_max = document.getElementById("ylimit_ax1_max").value;
    var ylimit_ax2_min = document.getElementById("ylimit_ax2_min").value;
    var ylimit_ax2_max = document.getElementById("ylimit_ax2_max").value;

    $.ajax("set_plot_amount", {
        contentType: "application/json",
        data: JSON.stringify({ ylimit_ax1_min: ylimit_ax1_min, ylimit_ax1_max: ylimit_ax1_max, ylimit_ax2_min: ylimit_ax2_min, ylimit_ax2_max: ylimit_ax2_max, amount: amount}),
        type: "POST",
        success: function(response) {}
    });
}
