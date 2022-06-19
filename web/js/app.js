/**
 * CONSTANTES
 */
const API_VERSION = '';
const BACKENDS = {
    'localhost': `http://localhost:8000/${API_VERSION}`
};

let hostname = window.location.hostname;
const BACKEND_URL = BACKENDS[hostname] ? BACKENDS[hostname] : `http://localhost:8000/${API_VERSION}`;


function call_api(what){
    return fetch(`${BACKEND_URL}${what}`).then(response => response.json())
        .catch(error => console.warn(error));
};

function ranking(){
    call_api("granted-benefits/ranking").then(response => {
        response.forEach(element => {
            console.log(element)
        });
    }).catch(error =>  console.warn(error));  
};
