if(!window.dash_clientside) {window.dash_clientside = {};}

window.dash_clientside.clientside = {
    toggle_modal: function (open_button, close_button, is_open) {
        if(open_button || close_button){
            return (!is_open)
        } else {
            return is_open
        }
    },
    toggle_collapse: function (n_clicks, is_open) {
        if(n_clicks) {
            return (!is_open)
        } else {
            return is_open
        }
    },
    disable_inputs_passabanda(checkbox) {
        if (checkbox.find(element => element == "Passa-Banda") == undefined) {
            return [true,true]
        } else {
            return [false, false]
        }
    },
    disable_inputs_savitzky(checkbox) {
        if (checkbox.find(element => element == "Filtro savitzky-golay") == undefined) {
            return [true,true]
        } else {
            return [false, false]
        }
    }
}


document.getElementById("upload-data").onmouseover = console.log("passou");