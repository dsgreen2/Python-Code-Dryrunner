
export function visualize(data){
    let x=data;
    x=JSON.parse(x);
    let editor=ace.edit("editorcode");
    document.getElementById("editorcode").style.display="none";

    let lines = editor.getValue().split('\n');
    let todisplaydiv=document.getElementById("todisplay");
    let codelist=document.createElement('ul');
    codelist.style.listStyleType="none";

    for(let i=0;i<lines.length;i++){
        let newline=document.createElement('li');
        newline.innerText=lines[i];
        codelist.append(newline);
    }

    todisplaydiv.append(codelist);
    todisplaydiv.style.display="block";
    
    let code=x["code"];
    let trace=x["trace"]; 
    console.log(trace);
    create_trace(code,trace);
    // changing the 1st column to show code as the slider moves.
   
  /*
   for(let i in x){
        if(i=="trace"){
            console.log("I am printing the trace here.");
            
            let tr=x[i];
            console.log(typeof(tr));
            for(let j in tr){
                console.log(j," = ",x[i][j]);
            }

        }
        else{
            console.log("I am printing the code here.");
            console.log(i," : ",x[i]);
        }
    }
    */
}

function configure_ace(lastline){

    let todisplaydiv=document.getElementById("todisplay");
    let linelist=todisplaydiv.getElementsByTagName('li');
    for(let i=0;i<linelist.length;i++){
        if(i==lastline-1){
            linelist[i].style.backgroundColor="grey";
        }
        else{
            linelist[i].style.backgroundColor="rgb(188, 194, 199)";
        }
    }

}

let idtohide=new Set();
function create_trace(code,trace){

    let dryrun_box=document.querySelector(".dryrun");
    let trace_area=document.createElement('div');
    dryrun_box.append(trace_area);
    trace_area.setAttribute('id','trace_box');

    let output_box=document.querySelector(".output");
    let output_area=document.createElement('div');
    output_box.append(output_area);

    window.ul_id=0;
    let no_of_steps=Object.keys(trace).length;
    let prevstdoutli=document.createElement('li');
    let prevstdoutid=-1;

    function printref(trace,ind,idofref){
        let k=trace[ind]["heap"][idofref];
        let toreturn='';
        let flag=0;
        console.log("-----------");
        console.log(idofref);
        //console.log(k.length);
        for(let index=0;index<k.length;index++){

            if(k[index]=="LIST"){
                toreturn+='[';
                flag=1;
                continue;
            }

            else if(k[index]=="DICT"){
                toreturn+='{';
                flag=2;
                continue;
            }

            else if(k[index]=="TUPLE"){
                toreturn+='(';
                flag=3;
                continue;
            }
            /*
            else if(k[index]=="REF"){
                index++;
                toreturn+=printref(trace,ind,k[index]);
            }*/

            if(typeof(k[index])=="object"){
                console.log("if");
                console.log(k[index][0]);
                console.log(k[index][1]);
                let recurans=printref(trace,ind,k[index][1]);
                if(index!=(k.length-1)){
                    toreturn=toreturn+' '+recurans+',';
                }

                else{
                    toreturn=toreturn+' '+recurans;
                }

                
            }
            else{
                console.log("else");
                console.log(k[index]);
                if(index!=(k.length-1)){
                toreturn+=' '+`${k[index]}`+',';
                }
                else{
                    toreturn+=' '+`${k[index]}`;
                }
            }
        }

        if(flag==1){
            toreturn+=' ]';
        }

        if(flag==2){
            toreturn+=' }';
        }
        if(flag==3){
            toreturn+=' )';
        }

        console.log(toreturn);

        return toreturn;
    }
    
    for (let ind in trace){

        if(ind==0) continue;
        let aa=document.createElement('ul');
        ul_id=ul_id+1;
        aa.setAttribute('id',ul_id);
        trace_area.append(aa);

        for(let i in trace[ind]["ordered_globals"]){
            if(trace[ind-1]["ordered_globals"].includes(trace[ind]["ordered_globals"][i])==false){

                let l=document.createElement('li');

                let ini_line='';

                let var_name=trace[ind]["ordered_globals"][i];

                for(let globals_ind in trace[ind]["globals"]){

                    if(globals_ind==var_name){
                        if(trace[ind]["globals"][globals_ind]==null){
                            ini_line+='Variable declared '+var_name+' null';
                        }
                        else if(typeof(trace[ind]["globals"][globals_ind])=="object"){

                           let ide=trace[ind]["globals"][var_name][1];

                                if(trace[ind]["heap"][ide][0]=='DICT'){
                                    ini_line+='Dictionary created '+var_name+' : { ';
                                    if(trace[ind]["heap"][ide].length<=11){
                                    for(let i=1;i<trace[ind]["heap"][ide].length;i++){

                                        ini_line+=`${trace[ind]["heap"][ide][i][0]}`+" : ";
                                        ini_line+=`${trace[ind]["heap"][ide][i][1]}`+" , ";
                                    }
                                    ini_line+=' } ';
                                }
                                }
                                else if(trace[ind]["heap"][ide][0]=='FUNCTION'){
                                    ini_line+="Function created "+trace[ind]["heap"][ide][1];
                                }
                                /*

                                else if(trace[ind]["heap"][ide][0]=='TUPLE'){
                                    ini_line+='Tuple created '+var_name+' :( ';
                                    if(trace[ind]["heap"][ide].length<=11){
                                        for(let i=1;i<trace[ind]["heap"][ide].length;i++){
                                            ini_line+=`${trace[ind]["heap"][ide][i]}`+' , ';
                                        }
                                    }

                                    ini_line+=')';

                                }

                                else if(trace[ind]["heap"][ide][0]=='LIST'){
                                    ini_line+='List created '+var_name+' :[ ';
                                    if(trace[ind]["heap"][ide].length<=11){
                                        for(let i=1;i<trace[ind]["heap"][ide].length;i++){
                                            ini_line+=`${trace[ind]["heap"][ide][i]}`+' , ';
                                        }
                                        ini_line+=']';
                                    }

                                }*/
                                else{
                                    ini_line+="Object created "+var_name+" : ";
                                    ini_line+=printref(trace,ind,ide);
                                }
                        }
                        else{
                            ini_line+='Variable declared '+var_name+' = '+trace[ind]["globals"][globals_ind];
                        }
                    }

                   /* for(let x in trace[ind]["heap"][globals_ind]){
                    console.log(trace[ind]["heap"][globals_ind][x]);
                    }
                    console.log(" ");

                    */
                }

                l.innerText=ini_line;
                aa.append(l);
            }

            else{      
                  //console.log("hello. in else");
                 let vname=trace[ind]["ordered_globals"][i];
                  //console.log(vname);
                  //console.log(trace[ind]["globals"][vname]);
                  //console.log(trace[ind-1]["globals"][vname]);
                 if(typeof(trace[ind]["globals"][vname])=="object"){
                    let vid=trace[ind]["globals"][vname][1];
                    for(let m=1;m<trace[ind]["heap"][vid].length;m++){
                        if(trace[ind]["heap"][vid][m]!=trace[ind-1]["heap"][vid][m]){
                            let lg=document.createElement('li');
                            let toshow='';
                            toshow+='Variable '+vname+' changed to ';

                            if(trace[ind]["heap"][vid][0]=='LIST'){
                                if(trace[ind]["heap"][vid].length<=11){
                                toshow+='[';
                                for(let pp=1;pp<trace[ind]["heap"][vid].length;pp++){
                                    toshow+=`${trace[ind]["heap"][vid][pp]}`+' , ';
                                }
                                toshow+=']';
                            }
                            }

                            else if(trace[ind]["heap"][vid][0]=='TUPLE'){
                               
                                if(trace[ind]["heap"][vid].length<=11){
                                    toshow+='(';
                                for(let pp=1;pp<trace[ind]["heap"][vid].length;pp++){
                                    toshow+=`${trace[ind]["heap"][vid][pp]}`+' , ';
                                }
                                toshow+=')';
                            }
                            }
                            
                            else if(trace[ind]["heap"][vid][0]=='DICT'){
                                
                                if(trace[ind]["heap"][vid].length<=11){
                                    toshow+='{ ';
                                   for(let pp=1;pp<trace[ind]["heap"][vid].length;pp++){

                                    toshow+=`${trace[ind]["heap"][vid][pp][0]}`+" : ";
                                    toshow+=`${trace[ind]["heap"][vid][pp][1]}`+" , ";
                                   }
                                    toshow+=' } ';
                                }

                            }

                            lg.innerText=toshow;
                            aa.append(lg);
                            break;
                        }
                    }
                }
               
                else if(trace[ind]["globals"][vname]!=trace[ind-1]["globals"][vname]){
                 //   console.log("Variable changed : "+vname+' '+trace[ind]["globals"][vname]);
                    let lg=document.createElement('li');
                    let toshow='';

                    
                    toshow+='Variable '+vname+' changed to '+trace[ind]["globals"][vname];
                    lg.innerText=toshow;
                    aa.append(lg);
                }
            }
        }
        
        if(trace[ind]["func_name"]!="<module>"){

            let stackdetails=trace[ind]["stack_to_render"][trace[ind]["stack_to_render"].length-1];
            let funcid=stackdetails["unique_hash"];
            let flagg=0;
            for(let previ=0;previ<trace[ind-1]["stack_to_render"].length;previ++){
                if(funcid==trace[ind-1]["stack_to_render"][previ]["unique_hash"]){
                    flagg=1;
                }
            }
            if(flagg){
                
                for(let vari=0;vari<stackdetails["ordered_varnames"].length;vari++){
                    
                    let varname=stackdetails["ordered_varnames"][vari];
                    let previndfunc;
                    
                    for(let previd=0;previd<trace[ind-1]["stack_to_render"].length;previd++){
                        if(funcid==trace[ind-1]["stack_to_render"][previd]["unique_hash"]){
                            previndfunc=trace[ind-1]["stack_to_render"][previd];
                            console.log("yes");
                            break;
                        }
                    }

                    console.log(previndfunc);
                    
                    if(previndfunc["ordered_varnames"].includes(varname)==false){
                        let loo=document.createElement('li');
                        let myini_line='';

                        

                        if(stackdetails["encoded_locals"][varname]==null){
                            myini_line+='Variable declared '+varname+' null';
                        }
                        
                        else if(typeof(stackdetails["encoded_locals"][varname])=="object"){

                            if(stackdetails["encoded_locals"][varname]=="__return__"){
                                myini_line+="Returning ";
                            }
                            
                            let oid=stackdetails["encoded_locals"][varname][1];
                            if(trace[ind]["heap"][oid][0]=='DICT'){
                                myini_line+='Dictionary created '+varname+' : { ';
                                
                                if(trace[ind]["heap"][oid].length<=11){
                                    
                                    for(let ii=1;ii<trace[ind]["heap"][oid].length;ii++){
                                        myini_line+=`${trace[ind]["heap"][oid][ii][0]}`+" : ";
                                        myini_line+=`${trace[ind]["heap"][oid][ii][1]}`+" , ";
                                    }
                                     myini_line+=' } ';
                                }
                            }
                        
                            else if(trace[ind]["heap"][oid][0]=='FUNCTION'){
                                myini_line+="Function created "+trace[ind]["heap"][oid][1];
                            }
                            
                            else{
                                myini_line+="Object created "+varname+" : ";
                                myini_line+=printref(trace,ind,oid);
                            }
                        }
                        else{
                            if(stackdetails["encoded_locals"][varname]=="__return__"){
                                myini_line+="Returning ";
                            }
                            myini_line+='Variable declared '+varname+' = '+stackdetails["encoded_locals"][varname];
                        }
                        
                        loo.innerText=myini_line;
                        aa.append(loo);
                    }
                    
                    else{
                        
                        if(typeof(stackdetails["encoded_locals"][varname])=="object"){
                            
                            let varid=stackdetails["encoded_locals"][varname][1];
                            for(let mn=1;mn<trace[ind]["heap"][varid].length;mn++){
                                
                                if(trace[ind]["heap"][varid][mn]!=trace[ind-1]["heap"][varid][mn]){
                                    let lig=document.createElement('li');
                                    let toshowg='';
                                    toshowg+='Variable '+varname+' changed to ';
                                
                                    if(trace[ind]["heap"][varid][0]=='LIST'){
                                        if(trace[ind]["heap"][varid].length<=11){
                                            toshowg+='[';
                                            for(let ppg=1;ppg<trace[ind]["heap"][varid].length;ppg++){
                                                toshowg+=`${trace[ind]["heap"][varid][ppg]}`+' , ';
                                            }
                                            toshowg+=']';
                                        }
                                    }
                                    
                                    else if(trace[ind]["heap"][varid][0]=='TUPLE'){
                                        
                                        if(trace[ind]["heap"][varid].length<=11){
                                            
                                            toshowg+='(';
                                            
                                            for(let ppg=1;ppg<trace[ind]["heap"][varid].length;ppg++){
                                                toshowg+=`${trace[ind]["heap"][varid][ppg]}`+' , ';
                                            }
                                            
                                            toshowg+=')';
                                        }
                                    }
                                    
                                    else if(trace[ind]["heap"][varid][0]=='DICT'){
                                        
                                        if(trace[ind]["heap"][varid].length<=11){
                                            
                                            toshowg+='{ ';
                                            
                                            for(let ppg=1;ppg<trace[ind]["heap"][varid].length;ppg++){
                                                toshowg+=`${trace[ind]["heap"][varid][ppg][0]}`+" : ";
                                                toshowg+=`${trace[ind]["heap"][varid][ppg][1]}`+" , ";
                                            }
                                            
                                            toshowg+=' } ';
                                        }
                                    }
                                    lig.innerText=toshowg;
                                    aa.append(lig);
                                }
                            }
                        }
                        
                        else{
                            if(stackdetails["encoded_locals"][varname]!=previndfunc["encoded_locals"][varname]){
                                let lig=document.createElement('li');
                                let toshowg='';
                                
                                toshowg+='Variable '+varname+' changed to '+stackdetails["encoded_locals"][varname];
                                lig.innerText=toshowg;
                                aa.append(lig);
                            }
                        }
                    }
                }
            }
        }

        if(trace[ind]["event"]=="exception"){
            let ld=document.createElement('li');
            let toappend='';
            toappend=trace[ind]["exception_msg"];
            ld.innerText=toappend;
            aa.append(ld);
        }

        if(trace[ind]["event"]=="call"){
            let l1=document.createElement('li');
            let dryrun_line='';
            dryrun_line+='Function called '+trace[ind]["func_name"]+'\n';
            dryrun_line+='Variables passed ';
            let ggtrace=trace[ind]["stack_to_render"][trace[ind]["stack_to_render"].length-1]["ordered_varnames"];
            for(let qq in ggtrace){
                if(qq!=ggtrace.length-1){
                    dryrun_line=dryrun_line+ggtrace[qq]+' : '+trace[ind]["stack_to_render"][trace[ind]["stack_to_render"].length-1]["encoded_locals"][ggtrace[qq]]+' , ';
                }
                else{
                    dryrun_line=dryrun_line+ggtrace[qq]+' : '+trace[ind]["stack_to_render"][trace[ind]["stack_to_render"].length-1]["encoded_locals"][ggtrace[qq]];
                }
            }
            dryrun_line+='\n';
            dryrun_line+="Inside "+trace[ind]["func_name"];

            console.log(dryrun_line);
            
            l1.innerText=dryrun_line;
            aa.append(l1);

        }

        if(trace[ind]["event"]=="return"&& trace[ind]["func_name"]!="<module>"){
            let l2=document.createElement('li');
            let line2='';
            line2+="Returning from "+trace[ind]["func_name"];
            l2.innerText=line2;
            aa.append(l2);
        }

        if(trace[ind]["stdout"].length>trace[ind-1]["stdout"].length){

            let st=trace[ind-1]["stdout"].length;

            if(st<1 || (trace[ind-1]["stdout"].endsWith("\n"))){
                let x=ul_id;
                let to_remove=document.getElementById(x);
                to_remove.parentNode.removeChild(to_remove);
                
                let ab=document.createElement('ul');
                ab.setAttribute('id',ul_id);
                output_area.append(ab);
                prevstdoutid=ul_id;
                //ab.classList.add("output");
               
                let l1=document.createElement('li');
                let curstdout='';
                for(let j=trace[ind-1]["stdout"].length;j<trace[ind]["stdout"].length;j++){
                    if(trace[ind]["stdout"][j]=='\\'){break;}
        
                    curstdout+=trace[ind]["stdout"][j];
                   // console.log(curstdout);
                }
                l1.innerText=curstdout;
                console.log("From if : "+l1.innerText);
                ab.append(l1);
                prevstdoutli=l1;
                //prevstdoutli=l1;
                // console.log("ID of this stdout : "+ul_id);

                let listItems2 =ab.getElementsByTagName('li');
                for (let i = 0; i < listItems2.length; i++) {
                    listItems2[i].style.fontFamily = 'Arial';
                    listItems2[i].style.color = 'rgb(126, 121, 121)';
                }
                ab.style.display="none";
              //  let aaaj=document.getElementById(ul_id);
                 //console.log("After setting display to none . I  retrieved the element by id ");
                //console.log(aaaj.innerHTML);
            }


            else{
                let x=ul_id;
                let to_remove=document.getElementById(x);
                to_remove.parentNode.removeChild(to_remove);
                let ab=document.createElement('ul');
                output_area.append(ab);
                ab.setAttribute('id',ul_id);
                ab.classList.add(prevstdoutid);
                //ab.classList.add("output");
                
                let addtoprev='';

                for(let j=st;j<trace[ind]["stdout"].length;j++){
                    if(trace[ind]["stdout"][j]=='\\'){break;}
                    addtoprev+=trace[ind]["stdout"][j];
                }

                idtohide.add(prevstdoutid);
                let prevline=document.getElementById(prevstdoutid);
                let txtofprev=prevline.innerText;
                console.log("From else");
                console.log("Old txt of prev : "+txtofprev);
                console.log("Text to add "+addtoprev);
                txtofprev+=addtoprev;
                ab.innerText=txtofprev;
                console.log("new txt of prev : "+ab.innerText);
                prevstdoutid=ul_id;

                let listItems1 =ab.getElementsByTagName('li');
                for (let i = 0; i < listItems1.length; i++) {
                    listItems1[i].style.fontFamily = 'Arial';
                    listItems1[i].style.color = 'rgb(126, 121, 121)';
                }
                ab.style.display="none";
            }

            continue;
        }

        let listItems =aa.getElementsByTagName('li');
        for (let i = 0; i < listItems.length; i++) {
            listItems[i].style.fontFamily = 'Arial';
            listItems[i].style.color = 'rgb(126, 121, 121)';
        }

        

        aa.style.display="none";
        
    }

      // console.log("calling adjust slider");
      // console.log("ul_id "+ul_id);
       adjust_slider(no_of_steps,trace);

}  





function adjust_slider(steps,trace){


    let slider = document.getElementById("slider");
    let prevButton = document.getElementById("prev-button");
    let nextButton = document.getElementById("next-button");

    slider.max=steps;
    slider.step=1; 
    slider.value=0;

    prevButton.addEventListener("click", () => {
        let currentValue = parseInt(slider.value);
        let prevValue = currentValue - 1;
        console.log("prev button clicked. till step "+slider.value);
        if (prevValue >= parseInt(slider.min)) {
          slider.value = prevValue; 
          if(slider.value>0){
          configure_ace(trace[slider.value-1]["line"]);   
          }  
          show_till_step(slider.value);
        }

      });

      nextButton.addEventListener("click", () => {
        let currentValue = parseInt(slider.value);
        let nextValue = currentValue + 1;
        console.log("currentvalue "+currentValue);
        console.log("next button clicked. till step "+slider.value);
        if (nextValue <= parseInt(slider.max)) {
          slider.value = nextValue;

          if(slider.value>0){
          configure_ace(trace[slider.value-1]["line"]);
          }
          show_till_step(slider.value);
          
        }
      });


}

function containsOnlyNumbers(str) {
    return /^[0-9]+$/.test(str);
}
  
               
function show_till_step(sliderval){
    console.log("Inside showtillstep");
    console.log("show till slider value "+sliderval);
    let tohide=null;
  
    for(let i=1;i<=sliderval;i++){
       let cur_line=document.getElementById(i);
        if(cur_line && cur_line.style.display==="none"){
            
            cur_line.style.display="block";
          
            console.log("showing curline of id : "+i);
            console.log("showing list item "+cur_line.innerHTML);
        }

        if(cur_line.style.display==="block"){

            if(i<sliderval && idtohide.has(i)){
                cur_line.style.display="none";
            }

        }
    }
    //console.log("slider max value "+slider.max);
    for(let i=Number(sliderval)+1;i<=slider.max;i++){
        let cur_line=document.getElementById(i);
      //  console.log("i : "+i);
        //console.log(cur_line.innerHTML);
        if(cur_line && cur_line.style.display==="none") continue;
        else if(cur_line){
            cur_line.style.display="none";
            console.log("hiding curline of id : "+i)
        }
    }
}