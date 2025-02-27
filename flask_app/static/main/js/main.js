let projects = {};
let currentIndex = 0;
let projectDiv = document.getElementById("featuredProjectContainer");

function LoadFeaturedProjects()
{
    var data_d = {};

    // GRAB DATA TO SERVER VIA jQuery.ajax({})
    jQuery.ajax({
        url: "/loadfeaturedprojects",
        data: data_d,
        type: "POST",
        success:function(returned_data){
            returned_data = JSON.parse(returned_data);
            // Create a new project for each project and put it in projects container =
            projects = returned_data['projects'];
            console.log(projects);

            LoadProject();
        }
    });
}

function NextProject() {

    if (projectDiv.children.length > 1) {
        let oldProject = projectDiv.children[1];


        oldProject.classList.remove("fade-in");
        oldProject.classList.add("fade-out");

        setTimeout(() => {
            if (oldProject.parentNode) {
                projectDiv.removeChild(oldProject);
            }
        }, 500); // Match transition duration
    }



    currentIndex++;
    if (currentIndex >= projects.length) {
        currentIndex = 0;
    }

    // Wait for fade-out to finish before loading new project
    setTimeout(() => {
        LoadProject();
    }, 500);
}

function LoadProject()
{
    if (projects.length === 0)
    {
        return;
    }

    let div = document.createElement("div");
    div.className = 'featuredProject';

    let a = document.createElement("a");
    a.className = "projectHeader";
    a.textContent = projects[currentIndex]['name'];

    let img = document.createElement("img");
    img.className = "projImg";
    img.src = "/static/main/images/" + projects[currentIndex]['image'];

    let a2 = document.createElement("a");
    a2.className = "projectDescription";
    a2.textContent = projects[currentIndex]['description'];

    div.appendChild(a);
    div.appendChild(img);
    div.appendChild(a2);


    projectDiv.insertBefore(div, projectDiv.children[1]);

    setTimeout(() => {
        div.classList.remove("fade-out");
        div.classList.add("fade-in");
    }, 50);
}


window.onload = function() {
    LoadFeaturedProjects();
};


setInterval(NextProject, 5000)