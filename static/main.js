var imageStorage = new Map();


/* == On-page routines == */

function formatThousands(val) {
    return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function updateBodyCounter() {
    const textarea = document.getElementById("issue-body-textarea");
    const curLength = textarea.value.length; 
    const maxLength = textarea.maxLength;
    const countStr = "(" + formatThousands(curLength) + "/" + formatThousands(maxLength) + ")"; 
    document.getElementById("body-length-tracker").innerHTML = countStr;
}

function updateImageCounter() {
    const countStr = "(" + imageStorage.size.toString() + "/4)";
    document.getElementById("image-number-tracker").innerHTML = countStr;
    if (imageStorage.size >= 4) {
        document.getElementById("add-image-button").disabled = true;
    } else {
        document.getElementById("add-image-button").disabled = false;
    };
}

function addImage() {
    /* Get and validate file */
    const file = document.getElementById("event-image-input").files[0];
    if (file.size > 2 * 1024 * 1024) {
        alert("Image is too chunky!");
        throw new Error("Image is too chunky!");
    }

    /* Append image to storage */
    if (imageStorage.has(file.name)) return;
    imageStorage.set(file.name, file);

    /* Count images and disable input */
    updateImageCounter();

    /* Prepare IDs */
    const buttonId = "remove-image-button-" + imageStorage.size.toString();
    const spanId = "image-span-" + imageStorage.size.toString()

    /* Prepare remove button */
    var removeButton = document.createElement("button");
    removeButton.textContent = "Remove";
    removeButton.setAttribute("id", buttonId);
    removeButton.setAttribute("class", "col-1 inline-button");
    removeButton.setAttribute("type", "button");
    removeButton.addEventListener("click", () => {
        document.getElementById(spanId).remove();
        document.getElementById(buttonId).remove();
        imageStorage.delete(file.name);
        updateImageCounter();
    });

    /* Prepare image span */
    var imageSpan = document.createElement("span");
    imageSpan.textContent = file.name;
    imageSpan.setAttribute("id", spanId);
    imageSpan.setAttribute("class", "col-7");

    /* Alter HTML */
    document.getElementById("image-list").appendChild(removeButton);
    document.getElementById("image-list").appendChild(imageSpan);
}

function saveForm() {
    document.getElementById("save-button").disabled = true;

    const elements = document.querySelectorAll(
        "#generator-form input[type=text],textarea,select"
    );
    elements.forEach((el) => {
        localStorage.setItem("muckracker-" + el.name, el.value);
    });

    document.getElementById("save-button").disabled = false;
}

function reloadForm() {
    var elements = document.querySelectorAll(
        "#generator-form input[type=text],textarea,select" 
    );
    elements.forEach((el) => {
        let value = localStorage.getItem("muckracker-" + el.name);
        if (value && value != "") el.value = value;
    });
}

function setFontSizes(elementId, min, max, step) {
    var element = document.getElementById(elementId);
    const sizes = Array.from(
        {length: (max - min) / step + 1},
        (val, indx) => min + indx * step
    );
 
    sizes.forEach((size) => {
        var optionElement = document.createElement("option");
        optionElement.setAttribute("value", size);
        optionElement.textContent = size + " pt";
        element.appendChild(optionElement);
    });
}

function onLoad() {
    setFontSizes("title-font-size-select", 32, 64, 2);
    setFontSizes("subtitle-font-size-select", 12, 32, 2);
    setFontSizes("details-font-size-select", 8, 18, 2);
    setFontSizes("body-titles-font-size-select", 8, 18, 2);
    setFontSizes("body-subtitles-font-size-select", 8, 18, 2);
    setFontSizes("body-text-font-size-select", 8, 18, 2);

    reloadForm();
    updateBodyCounter();

    document.getElementById("issue-body-textarea").addEventListener(
        "keyup", updateBodyCounter
    );
    document.getElementById("add-image-button").addEventListener(
        "click", () => document.getElementById("event-image-input").click()
    );
    document.getElementById("event-image-input").addEventListener(
        "change", addImage
    );
    document.getElementById("print-button").addEventListener(
        "click", generatePDF
    );
    document.getElementById("save-button").addEventListener(
        "click", saveForm
    );
}


/* == API interaction == */

function prepareIssue() {
    return JSON.stringify({
        config: {
            size: document.getElementById("size-select").value,
            bg: document.getElementById("bg-select").value
        },
        heading: {
            title: document.getElementById("title-input").value,
            subtitle: document.getElementById("subtitle-input").value,
            no: document.getElementById("issue-no-input").value,
            date: document.getElementById("issue-date-input").value,
            cost: document.getElementById("issue-cost-input").value
        },
        body: document.getElementById("issue-body-textarea").value
    });
}

async function generatePDF() {
    document.getElementById("print-button").disabled = true;

    var resp;
    var respJson;
    const resourceUrl = "/api/issue/";
    //const resourceUrl = "http://127.0.0.1:8001/issue/";

    try {
        resp = await fetch(resourceUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: prepareIssue()
        });
        respJson = await resp.json();
        if (resp.ok) var issueId = respJson.issue_id
        else throw new Error("Failed to send issue data");

        if (imageStorage.size > 0) {
            var formData = new FormData();
            imageStorage.forEach((file, key, map) => {
                formData.append("images", file, file.name);
            });
            resp = await fetch(resourceUrl + issueId, {
                method: "PATCH",
                body: formData
            });
            respJson = await resp.json();
            if (!resp.ok) throw new Error("Failed to send file");
        }

        resp = await fetch(resourceUrl + issueId, {method: "GET"});
        if (resp.ok) resp.blob().then(
            blob => window.open(URL.createObjectURL(blob))
        );
        else throw new Error("Failed to recieve PDF");
    } catch {
        console.error("Failed to generate PDF");
    } 

    document.getElementById("print-button").disabled = false;
}
