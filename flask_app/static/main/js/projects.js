function LoadFilters()
{
    var filtersContainer = document.getElementById("filtersInnerContainer");

    var data_d = {};
    
    // GRAB DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/loadfilters",
        data: data_d,
        type: "POST",
        success:function(returned_data){
                returned_data = JSON.parse(returned_data);
                // Create a new project for each project and put it in projects container =
                const keys = Object.keys(returned_data['filters']);

                for (let i = 0; i < keys.length; i++)
                {
                    const key = keys[i];

                    var div = document.createElement("div");
                    div.className = "filterDiv";

                    var input = document.createElement("input");
                    input.className = "filterCheckbox";
                    input.type = "checkbox";
                    input.setAttribute("data-skill", returned_data['filters'][key]['name']);

                    var a = document.createElement("a");
                    a.className = "filterText";
                    a.textContent = returned_data['filters'][key]['name'];
                    
                    div.appendChild(input);
                    div.appendChild(a);

                    filtersContainer.appendChild(div);

                    input.addEventListener("change", function() {
                        console.log("Checked Skills Updated:", getCheckedSkills()); // Debugging
                        LoadProjects();
                    });
                }
                // Ensure LoadProjects runs after skills are loaded
                setTimeout(() => {
                    LoadProjects();
                }, 10);
            }
    });
}

function getCheckedSkills() {
    return Array.from(document.querySelectorAll('.filterCheckbox:checked'))
        .map(checkbox => checkbox.dataset.skill); // Ensure dataset.skill is used
}

function LoadProjects()
{
    var projContainer = document.getElementById("projectsContainer");

    while (projContainer.firstChild) {
        projContainer.removeChild(projContainer.firstChild);
      }

    var data_d = {'filters': getCheckedSkills()};
    
    // GRAB DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/loadprojects",
        data: JSON.stringify(data_d),
        type: "POST",
        contentType: "application/json",
        success:function(returned_data){
                returned_data = JSON.parse(returned_data);
                // Create a new project for each project and put it in projects container =
                for (let project of returned_data['projects'])
                {
                    var div = document.createElement("div");
                    div.className = 'project';
                    div.addEventListener("click", function() {
                        window.location = String(project['link']);
                    });

                    var a = document.createElement("a");
                    a.className = "projectHeader";
                    a.textContent = String(project['name']);

                    var img = document.createElement("img");
                    img.className = "projImg";
                    img.src = "/static/main/images/" + String(project['image']);
                    

                    var a2 = document.createElement("a");
                    a2.className = "projectDescription";
                    a2.textContent = String(project['description']);

                    // Add child elements to project element
                    div.appendChild(a);
                    div.appendChild(img);
                    div.appendChild(a2);

                    projContainer.appendChild(div);
                }
            }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    LoadFilters();
  });