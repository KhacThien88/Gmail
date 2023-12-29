function hideAllEmailContainers() {
    const containers = ['emailInbox', 'emailProject', 'emailImportant', 'emailWork', 'emailSpam'];
    containers.forEach(containerId => {
      const container = document.getElementById(containerId);
      container.classList.remove('hidden');
      container.classList.add('hidden');
    });
}

function resetColorFolderButton() {
  const containers = ['buttonInbox', 'buttonProject', 'buttonImportant', 'buttonWork', 'buttonSpam'];
  containers.forEach(containerId => {
    const container = document.getElementById(containerId);
    if(container.classList)
    container.classList.remove('text-white');
    container.classList.remove('bg-gray-800');
    
  });
}

let isButtonPreviouslySelected = false;
function displayEmailsInFolder(folder) {
  fetch("/get-datas")
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error(`Network response was not ok: ${response.statusText}`);
      }
    })
    .then((datas) => {
      console.log(datas)
      const buttonFolder = document.getElementById(`button${folder}`);
  
      hideAllEmailContainers();
      const folderContainer = document.getElementById(`email${folder}`);
      folderContainer.classList.remove('hidden');
      const isButtonSelected = buttonFolder.classList.contains('bg-gray-800');

      resetColorFolderButton();

      if (isButtonSelected) {
        folderContainer.classList.add('hidden');
        isButtonPreviouslySelected = false;
      } else {
        buttonFolder.classList.add('bg-gray-800');
        buttonFolder.classList.add('text-white');
        folderContainer.classList.remove('hidden');
        isButtonPreviouslySelected = true;
      }

      folderContainer.innerHTML = '';
      let count = 1
      for (let i = 0; i < datas.length; i++) {
        const unreadStatus = datas[i].isCheck ? "" : "(Chưa đọc)";
        let emailItem = document.createElement("div");
        let emailItem1 = document.createElement("div");

        if (datas[i].forder == folder) {
          emailItem.innerHTML = `
          <div  class="flex p-2  border-2 border-gray-700 m-4 cursor-pointer hover:bg-gray-800 hover:text-white">      
          <div class="flex w-full" onclick="toggleEmailContent(i)">
              <p class="font-bold mr-5">${count}.</p>
              <p class="font-bold mr-5">${unreadStatus}</p>
              <p class="font-medium mr-5">${datas[i].sender},</p>
              <p class="">${datas[i].subject}</p>
              <i class="material-icons w-4 h-4 absolute right-0 mr-10">expand_more</i>
          </div>
          </div>`;

          emailItem1.innerHTML = `
          <div id="mail${i}" class="hidden mx-6" onclick="isCheck(${datas[i].EmailID})">
          <button class="material-icons absolute right-0 mr-10" onclick="moveEmailToFolder(${datas[i].EmailID})">menu</button>
          <div class="flex">
            <p class="font-bold mr-2">From:</p>
            <p>${datas[i].sender}</p>
          </div>
          <div class="flex">
            <p class="font-bold mr-2">Subject:</p>
            <p>${datas[i].subject}</p>
          </div>
          <div class="flex">
            <p class="font-bold mr-2">To:</p>
            <p>${datas[i].to}</p>
          </div>
          <div class="flex">
            <p class="font-bold mr-2">Cc:</p>
            <p>${datas[i].cc}</p>
          </div>
          <div class="mt-4">
            <p class="font-mono mr-2">${datas[i].content}</p>
          </div>
          <div class="flex items-center mt-2">
            <p class="font-bold mr-2 ">Tệp đính kèm:<\p>
            <ul class="flex">
            ${datas[i].attachment.map((attachment, index) => `
              <button class="underline mx-4 px-4 pb-1 border-2 border-gray-500 rounded-2xl text-bold hover:text-white hover:bg-gray-800" onclick="downloadAttachment(${attachment}, ${datas[i].base64content[index]})">
                ${attachment}
              </button>`
            ).join('')}
            </ul>
        </div>
          `;
          emailItem.addEventListener("click", (event) => {
            event.stopPropagation();
            toggleEmailContent(i);
          });

          folderContainer.appendChild(emailItem);
          folderContainer.appendChild(emailItem1);
          count = count + 1;
        }
      }
    })
    .catch((error) => {
      console.error("Error fetching data:", error);
    });
}

function toggleEmailContent(index) {
  const content = document.getElementById(`mail${index}`);
  content.classList.toggle('hidden');
}

function toggleEmailList() {
  emailListContainer.classList.toggle('hidden');
}

function downloadAttachment(attachment, base64Data) {
  console.log(attachment)
  console.log(base64Data)
  const blob = base64toBlob(base64Data);
  const fileName = attachment;
  const link = document.createElement('a');
  link.href = window.URL.createObjectURL(blob);
  link.download = fileName;
  link.click();
}

function base64toBlob(base64Data) {
  const byteCharacters = atob(base64Data);
  const byteNumbers = new Array(byteCharacters.length);
  
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }

  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray]);
}

function moveEmailToFolder(emailIndex) {
  const newTargetFolder = prompt('Chọn thư mục đích:');
  if (newTargetFolder !== null) {
    fetch("/update-folder", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify({ EmailID: emailIndex, newFolder: newTargetFolder}),
  }).then((_res) => {
      console.log('Email folder updated successfully.');
  });
  } 
  else {
      console.log('User canceled the operation.');
  }
}

function isCheck(emailIndex) {
    fetch("/update-isCheck", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify({ EmailID: emailIndex, isCheck: true}),
  }).then((_res) => {
      console.log('Email isCheck updated successfully.');
  });
}