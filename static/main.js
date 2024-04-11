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

function setFontSizes(elementId, min, max, step, defVal) {
    var element = document.getElementById(elementId);
    const sizes = Array.from(
        {length: (max - min) / step + 1},
        (val, indx) => min + indx * step
    );
 
    sizes.forEach((size) => {
        var optionElement = document.createElement("option");
        if (size == defVal) optionElement.setAttribute("selected", "selected");
        optionElement.setAttribute("value", size);
        optionElement.textContent = size + " pt";
        element.appendChild(optionElement);
    });
}

function onLoad() {
    setFontSizes("header-title-pt-select", 32, 64, 2, 48);
    setFontSizes("header-subtitle-pt-select", 8, 32, 2, 16);
    setFontSizes("header-details-pt-select", 8, 32, 2, 10);
    setFontSizes("main-title-pt-select", 8, 32, 2, 18);
    setFontSizes("main-subtitle-pt-select", 8, 32, 2, 14);
    setFontSizes("main-text-pt-select", 8, 32, 2, 10);

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
    page = {
        size: document.getElementById("size-select").value,
        bg: document.getElementById("bg-select").value
    };
    header = {
        title: document.getElementById("title-input").value,
        subtitle: document.getElementById("subtitle-input").value,
        no: document.getElementById("issue-no-input").value,
        date: document.getElementById("issue-date-input").value,
        cost: document.getElementById("issue-cost-input").value
    };
    body = document.getElementById("issue-body-textarea").value;
    fonts = {
        header_title_pt: document.getElementById("header-title-pt-select").value,
        header_subtitle_pt: document.getElementById("header-subtitle-pt-select").value,
        header_details_pt: document.getElementById("header-details-pt-select").value,
        main_title_pt: document.getElementById("main-title-pt-select").value,
        main_subtitle_pt: document.getElementById("main-subtitle-pt-select").value,
        main_text_pt: document.getElementById("main-text-pt-select").value
    } 

    return JSON.stringify({
        page: page,
        header: header,
        body: body, 
        fonts: fonts
    });
}

function startLoader() {
    var button = document.getElementById("print-button");
    var loaders = button.getElementsByClassName("loader");
    for (let loader of loaders) {
        loader.style.display = "inline-block";
    }
    button.disabled = true;
}

function stopLoader() {
    var button = document.getElementById("print-button");
    var loaders = button.getElementsByClassName("loader");
    for (let loader of loaders) {
        loader.style.display = "none";
    }
    button.disabled = false;
}

async function generatePDF() {
    startLoader();

    var resp;
    var respJson;
    const resourceUrl = "/api/issue/";

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

    stopLoader();
}
