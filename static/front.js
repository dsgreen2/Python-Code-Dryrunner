import {visualize} from "./visualize.js";

let editor=ace.edit("editorcode");
editor.container.style.height = "615px";

const runbtn=document.querySelector('.bttn');

let isreset=true;

document.addEventListener("DOMContentLoaded", function(event) { 
    document.getElementById("editbutton").click();
 });

const editbtn=document.querySelector('.bttn-2');

function sendData(){

    let input=document.getElementById("input-code").value;
    console.log(input);
}  


let editorlib={
    init(){
       //editor.setTheme("ace/theme/ambiance");
        editor.session.setMode("ace/mode/python");
    }
}
editorlib.init();


runbtn.addEventListener('click', ()=>{
    let user_entered_code=editor.getValue(); 
    isreset=false;
    

    fetch('/dryrun/',{
        method:'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
          },
         body:JSON.stringify(user_entered_code),
    })
    .then(function(response){
        return response.json();
    })
    .then(function(data){
        visualize(data);
    })
    .catch(function(error){
        console.log(error);
        console.error('There was a problem with the fetch operation ');
    });

});

function resetPage() {
    if (!isreset) { 
      location.reload();
      isreset = true; 
    }
}

let curval;
editbtn.addEventListener('click',()=>{
    
    let todisplayid=document.getElementById("todisplay");
    
/*
    let dryrunDiv = document.querySelector('.dryrun');
    let unorderedLists = dryrunDiv.querySelectorAll('ul');
    unorderedLists.forEach(ul => ul.remove());

    let outputdiv=document.querySelector('.output');
    let opunorderedLists = outputdiv.querySelectorAll('ul');
    opunorderedLists.forEach(ul => ul.remove());

    let sliderinp=document.getElementById("slider");
    sliderinp.value=sliderinp.defaultValue;
    sliderinp.max=sliderinp.defaultValue;
    sliderinp.min=sliderinp.defaultValue;
    sliderinp.step=sliderinp.defaultValue;
    
    editor.setValue(curval);
    */

    window.addEventListener("beforeunload", function() {
        curval=editor.getValue();
        console.log(curval);
      });
    
    resetPage();
    window.addEventListener("load", function() {
        editor=ace.edit("editorcode");
        editor.setValue("");
    });
    
    todisplayid.style.display="none";
    let editorcodeid=document.getElementById("editorcode");
    editorcodeid.style.display="block";

});


function getCookie(name) {

    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {

      const cookies = document.cookie.split(';');

      for (let i = 0; i < cookies.length; i++) {

        const cookie = cookies[i].trim();

        if (cookie.substring(0, name.length + 1) === (name + '=')) {

          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;

        }
      }
    }
    return cookieValue;
}




