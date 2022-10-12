import './model/application.mjs';
import User from './model/entity/user.mjs';
import client from './model/providers/http-client.mjs';



let currentPage = null;



function errorMessage(e){
    let messageBox = document.getElementById("error-message");
    messageBox.querySelector(".message").innerText = e.message;
    if (!messageBox.classList.contains("opened")){
        messageBox.classList.add("opened");
    }

    throw e;
}



async function showPropertyFormModal(resetForm=false){
    let propertyForm = document.querySelector("#users .dlg-properties");
    if (resetForm){
        propertyForm.reset();
    }
    if (!propertyForm.classList.contains("opened")){
        propertyForm.classList.add("opened");
    }

    let modalResult = await new Promise((resolve, reject) => {

        propertyForm.querySelector("[name=ok]").addEventListener("click", event => {
            event.preventDefault();
            resolve({
                "login": propertyForm.querySelector("[name=login]").value,
                "name": propertyForm.querySelector("[name=name]").value,
                "surname": propertyForm.querySelector("[name=surname]").value,
                "email": propertyForm.querySelector("[name=email]").value,
            });
        }, {once: true});

        propertyForm.querySelector("[name=cancel]").addEventListener("click", event => {
            event.preventDefault();
            resolve(false);
        }, {once: true});

    });

    if (propertyForm.classList.contains("opened")){
        propertyForm.classList.remove("opened");
    }

    return modalResult;
}


async function updateUser(lookup){
    try{
        let user = await User.get(lookup);
        let propertyForm = document.querySelector("#users .dlg-properties");
        propertyForm.querySelector("[name=login]").value = user.login;
        propertyForm.querySelector("[name=name]").value = user.name;
        propertyForm.querySelector("[name=surname]").value = user.surname;
        propertyForm.querySelector("[name=email").value = user.email;
        location.hash = `#${user.login}`;
        let updatedUserData = await showPropertyFormModal(false);
        location.hash = "";
        if (updatedUserData === false) return;
        Object.assign(user, updatedUserData);
        await user.update();
    } catch (e){
        errorMessage(e);
    } finally {
        await findUsers();
    }
}


async function deleteUser(event){
    try{
        event.preventDefault();
        let userId = event.target.dataset.userId;
        event.target.parentNode.innerText = "Deleting the user...";
        let user = await User.get(userId);
        await user.delete();
    } catch (e){
        errorMessage(e);
    } finally {
        await findUsers();
    }
}


async function findUsers(reload=true){
    let tableBody = document.querySelector("#users tbody");

    if (reload){
        let searchParams = {};
        let searchDlg = document.querySelector("#users .dlg-search");

        if (searchDlg.querySelector("[name=light-profile]").checked){
            searchParams.profile = "light";
        }

        let searchLine = searchDlg.querySelector("[name=search]").value;
        if (searchLine.length > 0){
            searchParams.q = searchLine;
        }

        try{
            currentPage = await User.find(searchParams);
        } catch (e){
            tableBody.innerHTML = "";

            let messageCell = document.createElement("td");
            messageCell.setAttribute("colspan", "6");
            messageCell.innerText = e.message;
            let messageRow = document.createElement("tr");
            messageRow.append(messageCell);
            tableBody.append(messageRow);
            
            throw e;
        }
    }

    document.querySelector("#users .ctrl-previous").disabled = currentPage.isFirstPage;
    document.querySelector("#users .ctrl-next").disabled = currentPage.isLastPage;

    tableBody.innerHTML = "";
    for (let user of currentPage){
        let userRow = document.createElement("tr");
        let actionsCell = document.createElement("td");

        let editLink = document.createElement("a");
        editLink.setAttribute("href", "#");
        editLink.innerText = "Edit";
        editLink.addEventListener("click", event => {
            event.preventDefault();
            let userId = event.target.dataset.userId;
            updateUser(userId);
        });
        editLink.dataset.userId = user.id;
        actionsCell.append(editLink);

        let node = document.createTextNode("\t");
        actionsCell.append(node);

        let removeLink = document.createElement("a");
        removeLink.setAttribute("href", "#");
        removeLink.innerText = "Remove";
        removeLink.addEventListener("click", deleteUser, {once: true});
        removeLink.dataset.userId = user.id;
        actionsCell.append(removeLink);
        userRow.append(actionsCell);

        let idCell = document.createElement("td");
        idCell.innerText = user.id || "";
        userRow.prepend(idCell);

        let loginCell = document.createElement("td");
        loginCell.innerText = user.login || "";
        idCell.after(loginCell);

        let nameCell = document.createElement("td");
        nameCell.innerText = user.name || "";
        actionsCell.before(nameCell);

        let surnameCell = document.createElement("td");
        surnameCell.innerText = user.surname || "";
        actionsCell.before(surnameCell);

        let emailCell = document.createElement("td");
        emailCell.innerText = user.email || "";
        actionsCell.before(emailCell);

        tableBody.append(userRow);
    }
}



window.addEventListener("load", async event => {

    let response = await fetch("/static/core/table.html");
    let table = await response.text();
    document.body.innerHTML = table;

    document.addEventListener("request", event => {
        console.log("Number of simultaneous requests: " + event.detail);
        document.getElementById("spinner").style.display = 'block';
    });

    document.addEventListener("response", event => {
        console.log("Number of simultaneous requests: " + event.detail);
        document.getElementById("spinner").style.display = 'none';
    });

    document.querySelector("#error-message .close-button").addEventListener("click", event => {
        event.preventDefault();
        let messageBox = document.getElementById("error-message");
        if (messageBox.classList.contains("opened")){
            messageBox.classList.remove("opened");
        }
    });

    document.querySelector("#users .ctrl-add").addEventListener("click", async event => {
        event.preventDefault();
        let modalResult = await showPropertyFormModal(true);
        if (modalResult === false) return;
        try{
            let user = new User(modalResult);
            await user.create();
        } catch (e){
            errorMessage(e);
        } finally {
            await findUsers();
        }
    });

    document.querySelector("#users .ctrl-next").addEventListener("click", async event => {
        event.preventDefault();
        await currentPage.next();
        await findUsers(false);
    });

    document.querySelector("#users .ctrl-previous").addEventListener("click", async event => {
        event.preventDefault();
        await currentPage.previous();
        await findUsers(false);
    });

    document.querySelector("#users .dlg-search [name=search]").addEventListener("input", async event => {
        await findUsers();
    });

    document.querySelector("#users .dlg-search").addEventListener("change", event => findUsers());

    let propertiesDlg = document.querySelector("#users .dlg-properties");
    let mouseX = null;
    let mouseY = null;

    propertiesDlg.addEventListener("mousedown", event => {
        if (document.elementFromPoint(event.clientX, event.clientY).nodeName !== "INPUT"){
            mouseX = event.clientX;
            mouseY = event.clientY;
        }
    });

    propertiesDlg.addEventListener("mousemove", event => {
        if (mouseX !== null && mouseY !== null){
            let deltaX = event.clientX - mouseX;
            let deltaY = event.clientY - mouseY;
            let rect = propertiesDlg.getBoundingClientRect();
            propertiesDlg.style.left = `${rect.x + deltaX}px`;
            propertiesDlg.style.top = `${rect.y + deltaY}px`;
            mouseX = event.clientX;
            mouseY = event.clientY;
        }
    });

    propertiesDlg.addEventListener("mouseup", event => {
        mouseX = null;
        mouseY = null;
    });

    function hashUpdate(){
        let hash = location.hash;
        if (hash.charAt(0) === '#'){
            hash = hash.slice(1);
        }
        let browserTitle = document.head.querySelector("title");
        if (hash){
            browserTitle.innerText = hash;
        } else {
            browserTitle.innerText = "User List";
        }
        if (!hash && propertiesDlg.classList.contains("opened")){
            propertiesDlg.classList.remove("opened");
        }
        if (hash && !propertiesDlg.classList.contains("closed")){
            updateUser(hash);
        }
    }

    window.addEventListener("hashchange", event => hashUpdate());

    await findUsers();
    hashUpdate();
});
