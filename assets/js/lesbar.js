// Deklaration von Variablen:
var AudioContext = window.AudioContext;
var audioContext;
var rec;
var gumStream;
var textwidth;
var stage;
var responsetype;
var textareaMaxWidth = Math.min(window.innerWidth * 0.85, 750);
var textareaWidth = Math.min(window.innerWidth * 0.85, 450);
var aussprache_ergebnis;
var letzteFarbigeAntwort;
var parameterUrl;
var sessionid;
var startTime;
var endTime;
var aufnahmeTimeout;
var audioObjectListenAgain;
const toggle_button = document.getElementById("toggle-record");
const mikrofonIcon = document.getElementById("mikrofonIcon");
const generierenButton = document.getElementById("generieren");
const textareaErrorMessage = document.getElementById('textarea-error');
const aufnehmenErrorMessage = document.getElementById('aufnehmen-fehlermeldung');
const abbrechen_wiederholen = document.getElementById('abbrechen-wiederholen');
const weiteruebenButton = document.getElementById('weiterueben');
const responseArea = document.getElementById('responseArea');
const responseText = document.getElementById('responseText');
const loadingSymbol = document.getElementById('loadingSymbol');
const waveform = document.getElementById('waveform');

const textarea = document.querySelector('.textarea-responsive');
const generator = document.querySelector('.generator');
const binIcon = document.querySelector('#clear');
const farbigeAntwort = document.querySelector('.farbigeAntwort');
const previousFeatureButton = document.querySelector('.previous-feature');
const nextFeatureButton = document.querySelector('.next-feature');



//TODO MITHILFE VON GLOBAL VARIABLEN ERST DEN STATE ABFRAGEN, BEVOR ETWAS VERSTECKT WIRD

// JQUERY?
const dropdown = $('.dropdown');

// Eventlisteners:
textarea.addEventListener('input', resizeTextArea);
window.addEventListener('resize', windowResize);

// TEXTAREA Funktionen
function resizeTextArea() {
    weiterueben_verstecken();
    hideWiederholen();
    aufnehmenErrorMessage.style.opacity = 0;
    aufnehmenErrorMessage.innerHTML = ""


    let computedFontSize = window.getComputedStyle(textarea).fontSize;
    let fontAttr = "400 " + String(Math.max(Math.min(parseInt(computedFontSize) + 1, 50), 30)) + "px Open Sans";
    textwidth = getTextWidth(textarea.value, fontAttr);
    // +computedFontSize wegen Padding von links & rechts
    textarea.style.width = Math.max(textareaWidth, Math.min(textwidth + (parseInt(computedFontSize) + 1), window.innerWidth * 0.95)) + 'px';

    textarea.style.height = '1.6em'; // wenn etwas gelöscht wird, geht es zurück auf die 48px
    textarea.style.height = textarea.scrollHeight + 'px';
    checkInput(textarea.value);
    toggleOpacityBinIcon();

    resize_responseArea();

}

function wordLen25(element, index, array) {
    return element.length > 25;
}

function stripText(text) {
    text = text.replace(/\s\s+/g, ' ').replace(/[`~!@#$%^&*()_|+\-=?;:'",.<>\{\}\[\]\\\/]/gi, '').trim();
    return text
}


function checkNumber(text) {
    return /\d/.test(text);
}


function checkNonGermanAlphabet(text) {
    return Boolean(text.match("[^a-zA-ZäöüÄÖÜß0-9 \s\x21-\x2F\x3A-\x40\x5B-\x60\x7B-\x7E]"))
}


function checkSpecialCharacterNotWroteOut(text) {
    return Boolean(text.match("[€\x23-\x26]"))
}

function checkInput(text) { // kein Wort darf über 25 Buchstaben sein
    raw_text = text
    text = stripText(text);
    let words = text.split(' ');
    textareaErrorMessage.innerHTML = "";
    if (words.some(wordLen25)) {
        textareaErrorMessage.innerHTML += "Kein Wort darf über 25 Buchstaben lang sein!";

    }
    if (checkNumber(text)) {
        textareaErrorMessage.innerHTML += " Bitte Zahlen ausschreiben! "
    }

    if (checkNonGermanAlphabet(raw_text)) {
        textareaErrorMessage.innerHTML += " Bitte verwende nur Buchstaben des deutschen Alphabets. "
    }

    if (checkSpecialCharacterNotWroteOut(raw_text)) {
        textareaErrorMessage.innerHTML += " Schreibe gesprochene Sonderzeichen aus "
        console.log("WHADLJ")
    }

    if (textareaErrorMessage.innerHTML != "") {
        toggle_button.style.pointerEvents = "none";
    } else {
        toggle_button.style.pointerEvents = "";
    }

    if (raw_text.length > 90) {
        if (raw_text.length == 119) {
            textareaErrorMessage.innerHTML += ` Noch 1 Buchstabe verbleibend. `
        } else {
            textareaErrorMessage.innerHTML += ` Noch ${120-raw_text.length} Buchstaben verbleibend. `
        }
    }

   





}

function getTextWidth(text, font) {
    // re-use canvas object for better performance
    const canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
    const context = canvas.getContext("2d");
    context.font = font;
    const metrics = context.measureText(text);
    return metrics.width;
}

// TEXTAREA JQUERY UNFOCUS ENTER
$('.textarea-responsive').keydown(function(e) {
    if (e.keyCode == 13) { //Enter gedrückt
        e.preventDefault();
        unfocus();
    }
});


// TEXTAREA + WINDOWRESIZE (siehe EVENTLISTENER)
function windowResize() {
    textareaMaxWidth = Math.min(window.innerWidth * 0.85, 750);
    textarea.style.maxWidth = textareaMaxWidth + 'px';
    textareaWidth = Math.min(window.innerWidth * 0.85, 450);
    textarea.style.width = textareaWidth + 'px';

    let computedFontSize = window.getComputedStyle(textarea).fontSize;
    let fontAttr = "400 " + String(Math.max(Math.min(parseInt(computedFontSize) + 1, 50), 30)) + "px Open Sans";
    textwidth = getTextWidth(textarea.value, fontAttr);
    textarea.style.width = Math.max(textareaWidth, Math.min(textwidth + (parseInt(computedFontSize) + 1), window.innerWidth * 0.95)) + 'px';

    textarea.style.height = '1.6em';
    textarea.style.height = textarea.scrollHeight + 'px';

    resize_responseArea();

}

// JQUREY DROPDOWN
dropdown.click(function() {

    $(this).attr('tabindex', 1).focus();
    $(this).toggleClass('active');
    $(this).find('.dropdown-menu').slideToggle(300);
});
$('.dropdown').focusout(function() {
    $(this).removeClass('active');
    $(this).find('.dropdown-menu').slideUp(300);
});
$('.dropdown .dropdown-menu li').click(function() {
    $(this).parents('.dropdown').find('span').text($(this).text());
    $(this).parents('.dropdown').find('input').attr('value', $(this).attr('content'));
});


//binIcon Funktion
function clearTextarea() {
    textarea.value = "";
    resizeTextArea();
    textarea.focus();
    weiterueben_verstecken();
}


function toggleOpacityBinIcon() {
    if (textarea.value.length < 7) {
        binIcon.onclick = "";
        binIcon.style.transition = "opacity 0s";
        binIcon.style.opacity = "0";
        binIcon.style.pointerEvents = "none";
    } else {
        binIcon.onclick = clearTextarea;
        binIcon.style.transition = "opacity 3s";
        binIcon.style.opacity = "1";
        binIcon.style.pointerEvents = "";

    }
}

//GENERIEREN (wenn generieren gedrückt wird)
function generieren() {
    let generierobjekt = dropdown.find('input').val();
    let response = satzGeneratorBackend(generierobjekt);
}

function satzGeneratorBackend(data) {
    parameterUrl = "/satzgenerator/?session=" + sessionid;
    console.log(parameterUrl)
    fetch(parameterUrl, {
        method: "post",
        body: data,
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            "TEXTAREAVALUE": textarea.value.replace(/\s+/g, ' ').trim(),
        },
    }).then(function(data) {
        data.text().then(text => {
            if (text.startsWith("<!DOCTYPE html>")) {
                document.open();
                document.write(text);
                document.close();
            }
            else {
            textarea.value = text;
            windowResize();
            resizeTextArea();}
        });
    });
}

// AUFNAHMEBUTTON FUNKTION
function togglerecord() {
    if (toggle_button.value == "bereit") {
        if (stripText(textarea.value).length > 1) {

            aufnehmenErrorMessage.style.opacity = 0;
            aufnehmenErrorMessage.innerHTML = ""
            console.log("STARTING RECORD");
            toggle_button.value = "aufnehmen...";
            record();

        } else {
            aufnehmenErrorMessage.style.opacity = 1;
            aufnehmenErrorMessage.innerHTML = "Bitte erst einen Übungssatz eingeben oder generieren!"
        }
    } else {
        console.log("STOPPING RECORD");
        end_recording();
    }
}

/*AUFNEHMEN*/
function record() {
    navigator.mediaDevices.getUserMedia({
        video: false,
        audio: true
    }).then(stream => {
        disableOther();
        weiterueben_verstecken();
        hideResponseArea();
        farbigeAntwort.innerHTML = "";

        mikrofonIcon.src = "static/assets/images/Mikrofon aktiv.svg";
        mikrofonIcon.style = "width: 80%; height: 80%; filter: invert(1);";
        let wave = new Wave();
        maximize_waveform();
        wave.fromStream(stream, "waveform", {
            type: "flower blocks",
            colors: ["#5c50fe", "#aa6bfd"]
                //colors: ["#aa6bfd", "green"]
        });
        audioContext = new AudioContext();
        gumStream = stream;
        /* use the stream */

        input = audioContext.createMediaStreamSource(stream);


        rec = new Recorder(input, {
            numChannels: 1
        });
        rec.record()

        toggleAbbrechen();
        display_remaining_record_time();


        aufnahmeTimeout = setTimeout(function() {
            console.log("TIMOUT");

            end_recording();
        }, 22000); // Maximale Aufnahmedauer: 22 Sekunden
    }).catch(err => {
        console.log("Error:" + err); // Permission denied
        aufnehmenErrorMessage.style.opacity = 1;
        aufnehmenErrorMessage.innerHTML = "Bitte erlaube den Zugriff auf das Mikrofon"
    });
};

function minimize_waveform() {
    waveform.style.width = "50%";
}

function maximize_waveform() {
    waveform.style.width = "330%";
}

const timer = ms => new Promise(res => setTimeout(res, ms))

async function display_remaining_record_time() {
    startTime = new Date();

    while (rec.recording) {
        endTime = new Date();
        var timeDifference = endTime - startTime; //in ms
        if (timeDifference > 15000) {
            aufnehmenErrorMessage.style.opacity = 1;
            aufnehmenErrorMessage.innerHTML = `Noch ${22 - Math.round(timeDifference /= 1000)} Sekunde(n) verbleibend`
        }
        await timer(500);

    }
}




/*AUFNAHME BEENDEN MIT SPEICHERN*/
function end_recording() {
    mikrofonIcon.src = "static/assets/images/Mikrofon.svg";
    mikrofonIcon.style = "filter: invert(1);";
    toggle_button.value = "bereit";
    aufnehmenErrorMessage.style.opacity = 0;
    aufnehmenErrorMessage.innerHTML = "";

    clearTimeout(aufnahmeTimeout);

    rec.stop();
    gumStream.getAudioTracks()[0].stop();
    rec.exportWAV(sendData);
    //toggleWiederholen();
    minimize_waveform();
    toggleAbbrechen();


}

/*REC ABBRECHEN*/
function rec_abbrechen() {
    gumStream.getAudioTracks()[0].stop();
    rec.stop();
    rec.clear();

    clearTimeout(aufnahmeTimeout);
    enableOther();

    mikrofonIcon.src = "static/assets/images/Mikrofon.svg";
    mikrofonIcon.style = "filter: invert(1);";
    toggle_button.value = "bereit";
    toggleAbbrechen();
    minimize_waveform();
}
/*WÄHREND DER AUFNAHME ANDERES AUSSCHALTEN*/
function disableOther() {
    binIcon.disabled = "disabled";
    generierenButton.disabled = "disabled";
    textarea.style.pointerEvents = "none";
}

function enableOther() {
    binIcon.disabled = "";
    generierenButton.disabled = "";
    textarea.style.pointerEvents = "";
}

// ABBRECHEN
function toggleAbbrechen() {
    if (rec.recording) {
        abbrechen_wiederholen.innerHTML = "abbrechen";
        abbrechen_wiederholen.onclick = rec_abbrechen;
        abbrechen_wiederholen.style.transition = "opacity 3s";
        abbrechen_wiederholen.style.opacity = "1";
        abbrechen_wiederholen.style.pointerEvents = "";
    } else {
        abbrechen_wiederholen.onclick = "";
        abbrechen_wiederholen.style.transition = "opacity 0.2s";
        abbrechen_wiederholen.style.opacity = "0";
        abbrechen_wiederholen.style.pointerEvents = "none";
    }
}


// WIEDERHOLEN
function wiederholen() {
    abbrechen_wiederholen.innerHTML = "abbrechen"
    abbrechen_wiederholen.onclick = rec_abbrechen;
    abbrechen_wiederholen.style.transition = "opacity 3s";
    abbrechen_wiederholen.style.opacity = "1";
    togglerecord();
    hideResponseArea();
}

function toggleWiederholen() {
    console.log("wiederholen");
    abbrechen_wiederholen.innerHTML = "wiederholen";
    abbrechen_wiederholen.onclick = wiederholen;
    abbrechen_wiederholen.style.transition = "opacity 3s";
    abbrechen_wiederholen.style.opacity = "1";
    abbrechen_wiederholen.style.pointerEvents = "";
    weiterueben_anzeigen();
}


function hideWiederholen() {
    abbrechen_wiederholen.onclick = "";
    abbrechen_wiederholen.style.transition = "opacity 0.2s";
    abbrechen_wiederholen.style.opacity = "0";
}

// WEITERÜBEN
function weiterueben() {
    enableOther();
    hideResponseArea();
    clearTextarea();
    weiterueben_verstecken();
}

function weiterueben_anzeigen() {
    weiteruebenButton.onclick = weiterueben;
    weiteruebenButton.style.transition = "opacity 3s";
    weiteruebenButton.style.opacity = "1";
    weiteruebenButton.style.pointerEvents = "";
}

function weiterueben_verstecken() {
    weiteruebenButton.onclick = "";
    weiteruebenButton.style.transition = "opacity 0.2s";
    weiteruebenButton.style.opacity = "0";
    weiteruebenButton.style.pointerEvents = "none";
}

// AUDIO RESPONSE TEXTAREA

function resize_responseArea() {
    responseArea.style.width = Math.min(parseFloat(textarea.style.width), parseInt(textarea.style.maxWidth)) + "px";
}



function show_responseArea() {


    //responseArea.style.height = Math.max(parseFloat(textarea.style.height) * 2.5, 250) + "px";
    //responseArea.style.display = "flex";
    responseArea.style.height = "auto";
    //responseArea.style.minHeight = (parseInt(textarea.style.height) + 50) + "px";
    responseArea.style.minHeight = "250px";
    //responseArea.style.overflow = "hidden";
    responseArea.style.visibility = "";
    responseArea.style.opacity = '1';
    responseArea.style.fontSize = (parseFloat(textarea.style.fontSize) / 1.5) + "px";

    responseText.style.opacity = "1";
}


function hideResponseArea() {
    responseArea.style.height = '0px';
    responseArea.style.minHeight = "0px";
    responseArea.style.visibility = "hidden";
    responseArea.style.opacity = "0";

    responseText.style.opacity = "0";
}

function updateResponseText(text) {
    responseText.innerHTML = text;
}



// ALLGEMEINE FUNKTIONEN
function unfocus() {
    var tmp = document.createElement("input");
    document.body.appendChild(tmp);
    tmp.focus();
    document.body.removeChild(tmp);
}

/* CRSF COOKIE ODER ANDEREN COOKIE BEKOMMEN */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/* AUDIO ZUM ERNEUTEN ANHÖREN BEREITSTELLEN */
function createAudioObject(blob) {
    var url = URL.createObjectURL(blob);
    audioObjectListenAgain = document.createElement('audio');

    //add controls to the <audio> element
    audioObjectListenAgain.controls = true;
    audioObjectListenAgain.src = url;
}










/* AUDIO ANS BACKEND SENDEN */

function sendData(data) {
    createAudioObject(data);
    show_responseArea();

    console.log("Sendet Audio Dateien ans Backend")
    parameterUrl = "/audio/?session=" + sessionid;

    console.log(parameterUrl)
    fetch(parameterUrl, {
        method: "post",
        body: data,
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            "TARGETSATZ": encodeURIComponent(textarea.value.replace(/\s+/g, ' ').trim()),
        },

    }).then(function(data) {
        data.text().then(text => {
            if (text == "Audio_to_short") {
                
                aufnehmenErrorMessage.style.opacity = 1;
                aufnehmenErrorMessage.innerHTML = "Die aufgenommene Audio ist zu kurz. Bitte erneut versuchen!"
                hideResponseArea();
                enableOther();
            } else if (text == "Fehler_Targetsatz") {
                aufnehmenErrorMessage.style.opacity = 1;
                aufnehmenErrorMessage.innerHTML = "Fehler beim Targetsatz erhalten. Bitte einen anderen Satz lernen."
                hideResponseArea();
                enableOther();
            } else if (text == "Audio_unnormal_length") {
                aufnehmenErrorMessage.style.opacity = 1;
                aufnehmenErrorMessage.innerHTML = "Fehler beim Aufnehmen der Audio. Bitte erneut versuchen oder die Seite neu laden."
                hideResponseArea();
                enableOther();
            } else {
                console.log(text);
                stage += 1;
                recursiveresponse();
                loadingSymbol.style.opacity = 1;
                responseText.style.width = "50%";
                disableOther();
                toggle_button.style.pointerEvents = "none";
                updateResponseText("Audio an AusspracheTrainerIPAKI, Google und IBM senden...");

            }
        });

    });
}

/* ERHÄLT AUDIO TRANSKRIPT INFOS (irreführender Name, hat nichts mit rekursiv zu tun) */

function recursiveresponse() {
    parameterUrl = "/recursiveresponse/?session=" + sessionid;

    fetch(parameterUrl, {
        method: "post",
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
        },
    }).then(function(data) {
        updateResponseText("Aussprache wird analysiert...");

        data.text().then(text => {
            loadingSymbol.style.opacity = 0;
            responseText.style.width = "100%";
            $("#responseText").html(text);
            responseText.insertBefore(audioObjectListenAgain, responseText.children[1]);
            toggleWiederholen();
            toggle_button.style.pointerEvents = "";
        });
    });
}

/* TRANSKRIPT DETAILS (wenn man auf einen Button drückt beim Ergebnis) */
function get_AT_transcript() {
    parameterUrl = "/get_other_transcripts/?session=" + sessionid;

    fetch(parameterUrl, {
        method: "post",
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            "KITYP": "AT",
        },
    }).then(function(data) {

        data.text().then(text => {
            letzteFarbigeAntwort = $(".farbigeAntwort-container").html();
            text = JSON.parse(text);
            console.log(text);

            textarea.value = text[1];
            $(".farbigeAntwort-container").html(text[0]);
        });
    });
}

function get_GOOGLE_transcript() {
    parameterUrl = "/get_other_transcripts/?session=" + sessionid;

    fetch(parameterUrl, {
        method: "post",
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            "KITYP": "GOOGLE",
        },
    }).then(function(data) {

        data.text().then(text => {
            letzteFarbigeAntwort = $(".farbigeAntwort-container").html();
            $(".farbigeAntwort-container").html(text);
        });
    });
}

function get_IBM_transcript() {
    parameterUrl = "/get_other_transcripts/?session=" + sessionid;

    fetch(parameterUrl, {
        method: "post",
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            "KITYP": "IBM",
        },
    }).then(function(data) {

        data.text().then(text => {
            letzteFarbigeAntwort = $(".farbigeAntwort-container").html();
            $(".farbigeAntwort-container").html(text);
        });
    });
}

function textarea_to_old_rawtarget() {
    parameterUrl = "/get_other_transcripts/?session=" + sessionid;

    fetch(parameterUrl, {
        method: "post",
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
            "KITYP": "TARGET",
        },
    }).then(function(data) {

        data.text().then(text => {
            console.log(text);

            textarea.value = text;
        });
    });
}


function get_raw_textarea_value_backend() {
    parameterUrl = "/buchstaben_scores/?session=" + sessionid;

    fetch(parameterUrl, {
        method: "post",
        headers: {
            "X-CSRFToken": getCookie('csrftoken'),
        },
    }).then(function(data) {

        data.text().then(text => {
            $(".farbigeAntwort-container").html(text);
        });
    });
}


function KITYP_onpointerup() {
    get_raw_textarea_value_backend();
    textarea_to_old_rawtarget();
}





//JQUERY
/* PAGE LOAD */
(function($) {

    "use strict";
    // VERSTANDEN
    // Page loading animation; Nicht löschen, sagt der Preloader animation, wann die Seite fertig geladen hat.
    $(window).on('load', function() {
        $('#js-preloader').addClass('loaded');
        sessionid = makeid();
        textarea.value = "";
        resizeTextArea();
    });

})(window.jQuery);

/* SESSION ID */

// https://stackoverflow.com/questions/48095737/django-new-session-for-each-browser-tab/48112774
function makeid() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for (var i = 0; i < 6; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
}


/* FEATURE SLIDEBAR */

function features_forward() {
    var features = document.querySelectorAll(".feature");
    var activeIndicators = document.querySelectorAll(".active-indicator");
    var active_feature = document.querySelector(".feature.active");
    for (var i = 0; i < features.length; i++) {
        if (features[i] == active_feature) {
            active_feature.classList.remove("active");
            activeIndicators[i].classList.remove("active");
            active_feature.style.transform = "translateX(-60%) scale(0.98)";
            setTimeout(function() {
                active_feature.style.transform = "";
            }, 300)
            if (i + 1 == features.length) {
                features[0].classList.add("active");
                activeIndicators[0].classList.add("active");

                break;
            }
            features[i + 1].classList.add("active");
            activeIndicators[i + 1].classList.add("active");

            break;
        }

    }
}


function features_backward() {
    var features = document.querySelectorAll(".feature");
    var activeIndicators = document.querySelectorAll(".active-indicator");
    var active_feature = document.querySelector(".feature.active");
    for (var i = 0; i < features.length; i++) {
        if (features[i] == active_feature) {
            active_feature.classList.remove("active");
            activeIndicators[i].classList.remove("active");
            active_feature.style.transform = "translateX(-40%) scale(0.98)";
            setTimeout(function() {
                active_feature.style.transform = "";

            }, 300)
            if (i == 0) {
                features[features.length - 1].classList.add("active");
                activeIndicators[features.length - 1].classList.add("active");
                break;
            }
            features[i - 1].classList.add("active");
            activeIndicators[i - 1].classList.add("active");

            break;
        }
    }
}


/* ON HOVER FUNKTION FÜR DIE FEATURE BUTTONS */



previousFeatureButton.addEventListener("pointerover", function() {
    previousFeatureButton.innerHTML = "&#171;";
});
previousFeatureButton.addEventListener("pointerout", function() {
    previousFeatureButton.innerHTML = "&#8249;";
});


nextFeatureButton.addEventListener("pointerover", function() {
    nextFeatureButton.innerHTML = "&#187;";
});
nextFeatureButton.addEventListener("pointerout", function() {
    nextFeatureButton.innerHTML = "&#8250;";

});


/* COOKIE LAW (package deinstalliert;) CODE ÄNDERN!! */
var Cookielaw = {
    ACCEPTED: '1',
    REJECTED: '0',

    createCookie: function(name, value, days) {
        var date = new Date(),
            expires = '';
        if (days) {
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toGMTString();
        } else {
            expires = "";
        }
        document.cookie = name + "=" + value + expires + "; path=/";
    },

    createCookielawCookie: function(cookieValue) {
        cookieValue = cookieValue || this.ACCEPTED;
        this.createCookie('cookielaw_accepted', cookieValue, 10 * 365);

        if (typeof(window.jQuery) === 'function') {
            jQuery('#CookielawBanner').slideUp();
        } else {
            document.getElementById('CookielawBanner').style.display = 'none';
        }
    },

    accept: function() {
        this.createCookielawCookie(this.ACCEPTED);
    },

    reject: function() {
        this.createCookielawCookie(this.REJECTED);
    }
};