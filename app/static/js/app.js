const uploadBtn = document.getElementById('upload');
const fileInput = document.getElementById('fileInput');
const upActions = document.getElementById('upActions');
const upSend= document.getElementById('upSend');
const upDelete= document.getElementById('upDelete');
const upLoadMusic= document.getElementById('upLoadMusic');
const transcriptionBody= document.getElementById('transcriptionBody');

uploadBtn.addEventListener('click',() => fileInput.click());

fileInput.addEventListener('change',() => {
    const file = fileInput.files[0];

    if(!file) return;

    upLoadMusic.removeAttribute('hidden');
    upActions.removeAttribute('hidden');
    
});

upSend.addEventListener('click',() => {
    sendFile(uploadedFile);
});

upDelete.addEventListener('click',() => {

});

function sendFile(file){
    const formData = new FormData();
    formData.append('audio',file);
    const xhr = new XMLHttpRequest();
    xhr.open('POST','/api/voice/upload',true);
    xhr.upload.onprogress=(event)=>{
        if(event.lengthComputable){
            const percent = Math.round(
                (event.loaded / event.total) * 100
            );
            console.log(`Uploaded: ${percent}`)
        }
    };
    xhr.onload = () => {
        if(xhr.status>= 200 && xhr.status < 300){
            console.log(`Success:`,JSON.parse(xhr.responseText));
        }else{
            console.log('server error:', xhr.status)
        }
        xhr.onerror = () => {
            console.log('network error')
        };
    }
    xhr.send(formData)
}