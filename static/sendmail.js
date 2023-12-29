function openSendMail() {
      const sendmail = document.getElementById('sendmail');
      sendmail.classList.remove('hidden');
      sendmail.classList.add('flex');
}

function clearFileInput() {
  const subjectInput = document.getElementById('subject');
  const toInput = document.getElementById('to');
  const ccInput = document.getElementById('cc');
  const bccInput = document.getElementById('bcc');
  const messageInput = document.getElementById('message');
  
  subjectInput.value = '';
  toInput.value = '';
  ccInput.value = '';
  bccInput.value = '';
  messageInput.value = '';

  const fileNamesDisplay = document.getElementById('fileNamesDisplay');
  fileNamesDisplay.innerHTML = '';
}

function closeSendMail() {
  const sendmail = document.getElementById('sendmail');
  sendmail.classList.add('hidden');
  clearFileInput();
}

window.addEventListener("load", () => {
    const input = document.getElementById("fileInput");
    const filewrapper = document.getElementById("filewrapper");
    
    input.addEventListener("change", (e) => {
        let filename = e.target.files[0].name;
        fileshow(filename);
    });
  
    const fileshow = (filename) => {
        let showfileboxElem = document.createElement("div");
        showfileboxElem.classList.add("flex");
        showfileboxElem.classList.add("border-2");
        showfileboxElem.classList.add("rounded");
        showfileboxElem.classList.add("px-1");

        showfileboxElem.innerHTML = `
            <p class="text-sm font-bold">${filename}</p>
        `;
        icon = document.createElement("div");
        icon.innerHTML = `
        <button class="material-symbols-outlined bg-red-500">close_small</button>
        `;

        showfileboxElem.append(icon)
        filewrapper.appendChild(showfileboxElem);

        icon.addEventListener("click", () => {
            filewrapper.removeChild(showfileboxElem);
        });
    };
});

  