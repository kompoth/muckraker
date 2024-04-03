function formatThousands(val) {
    return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function trackBodyLenght () {
    const textarea = document.getElementById("issue-body-textarea");
    const curLength = textarea.value.length; 
    const maxLength = textarea.maxLength;
    const countStr = "(" + formatThousands(curLength) + "/" + formatThousands(maxLength) + ")"; 
    document.getElementById("body-length-tracker").innerHTML = countStr;
}

function updateImageList() {
    var imageInput = document.getElementById("image-input");
    var BreakException = {};
    try {
        Array.from(imageInput.files).forEach((file) => {
            if (file && file.size > 2 * 1024 * 1024) throw BreakException;
        });
    } catch(exc) {
        if (exc != BreakException) throw exc;
        imageInput.value = null;
        alert("Image is too chunky!");
    }
    
    const countImages = Math.min(4, imageInput.files.length);
    const countStr = "(" + countImages.toString() + "/4)";
    document.getElementById("image-number-tracker").innerHTML = countStr;

    var imageList = document.getElementById("attached-images-list");
    imageList.innerHTML = "";
    Array.from(imageInput.files).slice(0, countImages).forEach((file) => {
        var li = document.createElement("li");
        li.innerHTML = file.name;
        imageList.appendChild(li);    
    });
}

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

        const imageInput = document.getElementById("image-input");
        if (imageInput.files.length > 0) {
            var formData = new FormData();
            Array.from(imageInput.files).slice(0, 4).forEach((file) => {
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
