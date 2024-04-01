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
    const imageInput = document.getElementById("image-input");
    const countImages = Math.min(4, imageInput.files.length);
    const countStr = "(" + countImages.toString() + "/4)";
    document.getElementById("image-number-tracker").innerHTML = countStr;
    
    var imageList = document.getElementById("attached-images-list");
    imageList.innerHTML = "";
    Array.from(imageInput.files).slice(0, 4).forEach((file) => {
        var li = document.createElement("li");
        li.innerHTML = file.name;
        imageList.appendChild(li);    
    });
}

async function requestPDF() {
    document.getElementById("print-button").disabled = true;
 
    const requestBody = {
        config: {
            size: document.getElementById("size-select").value,
            bg: document.getElementById("bg-select").value,
            heading: {
                title: document.getElementById("title-input").value,
                subtitle: document.getElementById("subtitle-input").value,
                no: document.getElementById("issue-no-input").value,
                date: document.getElementById("issue-date-input").value,
                cost: document.getElementById("issue-cost-input").value
            }
        },
        body: document.getElementById("issue-body-textarea").value
    }

    try {
        const resp = await fetch("/api/issue", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "accept": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        if (resp.ok) {
            /* If everything is ok, open recieved PDF */
            resp.blob().then(blob => window.open(URL.createObjectURL(blob)));
        }
    } catch {
        console.error("Failed to get PDF");
    }

    document.getElementById("print-button").disabled = false;
}
