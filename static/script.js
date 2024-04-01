function formatThousands(val) {
    return val.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function trackBodyLenght () {
    const textarea = document.getElementById("issue-body-textarea");
    const curLength = textarea.value.length; 
    const maxLength = textarea.maxLength;
    const countStr = formatThousands(curLength) + "/" + formatThousands(maxLength); 
    document.getElementById("body-length-tracker").innerHTML = countStr;
}

function updateImageList () {
    const imageInput = document.getElementById("image-input");
    var imageList = document.getElementById("attached-images-list");
    imageList.innerHTML = "";
    Array.from(imageInput.files).forEach((file) => {
        var li = document.createElement("li");
        li.innerHTML = file.name;
        imageList.appendChild(li);    
    });
}

async function requestPDF() {
    document.getElementById("print-button").disabled = true;

    const requestBody = {
        config: {
            bg: "bashcorpo_v5_pale",
            size: "demitab",
            heading: {
                title: document.getElementById("heading-input").value,
                subtitle: document.getElementById("subheading-input").value,
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
