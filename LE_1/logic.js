function saveContact(form){
    try{
        const name = form.name.value;
        const number = form.number.value

        const contact = {
        name: name,
        number: number
        }

        let contacts = localStorage.getItem('contacts');
        if (contacts){
            contacts = JSON.parse(contacts);
        }else{
            contacts = [];
        }
        contacts.push[contact]
        contactsJson = JSON.stringify(contacts);
        localStorage.setItem('contacts', contactsJson);

        console.log(contact);
    }
    catch(error){
        console.error("Error saving contacts:", error);
        return;
    }
    finally{
        form.reset();
    }
}
function loadContact(form){
    try{
        let name = form.name.value;

        let contacts = localStorage.getItem('contacts');
        if(contacts){
            contacts = JSON.parse(contacts);
        }else{
            return;
        }
        contacts = contacts.filter(c => c.name === name);

        let className = "";
        let cnt = 0;
        for(let index in contacts)
            if (cnt % 2 == 0){
                className = 'rowEven';
            }else{
                classnName = 'rowOdd';
            }
            document.getElementById('output').innerHTML += '<div calss='${className}""
            cnt++



        innerHTML.output =
    }
    catch(error){
        console.error("Error",error);
    }
    finally{
        form.reset();
    }
}
