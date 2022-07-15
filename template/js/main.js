const fileInput = $(".custom-file-input");
const audioElement = $(".output audio");
const btnSubmit = $(".btn-submit");
const btnLoading = $(".btn-loading");
const outputElement = $(".output");
const outputText = $(".output__text");

let file, fileURL;
let fileReader = new FileReader();

fileInput.on("change", function () {
    file = $(this).prop("files")[0];

    var fileName = $(this).val().split("\\").pop();
    $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
});

btnSubmit.click((event) => {
    event.preventDefault();
    if (!file) {
        alert("Please upload your audio!");
    } else {
        btnSubmit.hide();
        btnLoading.show();

        displayAudioElement(file.type);

        const formData = new FormData();
        formData.append("file", file);

        const xhr = new XMLHttpRequest();

        xhr.open("POST", "/upload/audio", true);
        xhr.send(formData);

        xhr.onreadystatechange = function () {
            if (xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200) {
                btnSubmit.show();
                btnLoading.hide();

                const data = JSON.parse(xhr.responseText);
                outputText.text(data);
            }
        };
    }
});

const displayAudioElement = function (fileType) {
    let validExtensions = ["audio/wav", "audio/mp3"];

    if (!validExtensions.includes(fileType)) {
        alert("This file is not supported!");
    } else {
        fileReader.onload = () => {
            let fileURL = fileReader.result;
            audioElement.attr("src", fileURL);
        };
        fileReader.readAsDataURL(file);

        outputElement.show();
    }
};

// const voiceRecognition = async (formData) => {
//     const response = await fetch("http://127.0.0.1:8000/upload/audio", {
//         method: "POST",
//         body: formData,
//         headers: {
//             "Content-Type": "application/json",
//         },
//     });
//     const myJson = await response.json();
//     console.log(myJson);
// };
