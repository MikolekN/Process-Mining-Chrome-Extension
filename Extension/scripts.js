const saveFile = async function(blob, suggestedName) {
    // Feature detection. The API needs to be supported
    // and the app not run in an iframe.
    const supportsFileSystemAccess =
        'showSaveFilePicker' in window &&
        (() => {
            try {
                return window.self === window.top;
            } catch {
                return false;
            }
        })();
    // If the File System Access API is supported…
    if (supportsFileSystemAccess) {
        try {
            // Show the file save dialog.
            const handle = await showSaveFilePicker({
                suggestedName,
            });
            // Write the blob to the file.
            const writable = await handle.createWritable();
            await writable.write(blob);
            await writable.close();
            return;
        } catch (err) {
            // Fail silently if the user has simply canceled the dialog.
            if (err.name !== 'AbortError') {
                console.error(err.name, err.message);
                return;
            }
        }
    }
    // Fallback if the File System Access API is not supported…
    // Create the blob URL.
    const blobURL = URL.createObjectURL(blob);
    // Create the "a" element and append it invisibly.
    const a = document.createElement('a');
    a.href = blobURL;
    a.download = suggestedName;
    a.style.display = 'none';
    document.body.append(a);
    // Click the element.
    a.click();
    // Revoke the blob URL and remove the element.
    setTimeout(() => {
        URL.revokeObjectURL(blobURL);
        a.remove();
    }, 1000);
};

const createTableTh = function(content, className) {
    const th = document.createElement("th");
    th.setAttribute("scope", "col");
    if (typeof className !== undefined) {
        th.setAttribute("class", className);
    }
    th.textContent = content;

    return th;
}

const createTable = function(className) {
    const table = document.createElement("table");
    table.setAttribute("class", className);
    const thead = document.createElement("thead");
    const tr = document.createElement("tr");
    
    const th1 = createTableTh("Event ID", "tab-head");
    const th2 = createTableTh("Ref Event ID", "tab-head");
    const th3 = createTableTh("Page Title");
    //const th4 = createTableTh("");
    tr.appendChild(th1);
    tr.appendChild(th2);
    tr.appendChild(th3);
    //tr.appendChild(th4);
    thead.appendChild(tr);
    
    table.appendChild(thead);

    return table;
}

const createMainRow = function(idx) {
    const row = document.createElement("tr");
    row.setAttribute("class", "accordion-toggle collapsed");
    row.setAttribute("id", "accordion" + idx);
    row.setAttribute("data-bs-toggle", "collapse");
    row.setAttribute("data-bs-parent", "#accordion" + idx);
    row.setAttribute("href", "#collapse" + idx);
    row.setAttribute("aria-controls", "collapse" + idx);

    return row;
}

const createDetailsDiv = function(label, content) {
    const div1 = document.createElement("div");
    div1.setAttribute("class", "col-2");
    div1.textContent = label;
    const div2 = document.createElement("div");
    div2.setAttribute("class", "col-6");
    div2.textContent = content;
    const div3 = document.createElement("div");
    div3.setAttribute("class", "row");
    div3.appendChild(div1);
    div3.appendChild(div2);

    return div3;
}

const createDivider = function() {
    const hr = document.createElement("hr");
    hr.setAttribute("class", "divider-line");

    return hr;
}

const formatDateElement = function(value) {
    if (value < 10) {
        value = "0" + value.toString();
    }

    return value;
}

const getDateFromTimestamp = function(timestamp) {
    let eventDate = new Date(timestamp);
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    let year = eventDate.getFullYear();
    let month = months[eventDate.getMonth()];
    let date = eventDate.getDate();

    let hour = formatDateElement(eventDate.getHours());
    let min = formatDateElement(eventDate.getMinutes());
    let sec = formatDateElement(eventDate.getSeconds());

    return date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec;
}

const getDuration = function(duration) {
    let durationSec = duration / 1000;

    return durationSec.toString() + " s";
}

const removeElementById = function(id) {
    if (document.contains(document.getElementById(id))) {
        document.getElementById(id).remove();
    }
}

const createVisualisationImage = function(blob) {
    const imgUrl = window.URL.createObjectURL(blob);
    let img = document.createElement('img');
    img.setAttribute("id", "visualisation-graph");
    img.src = imgUrl;
    document.getElementById("zoom").appendChild(img);
}

const displayVisualisationImage = function(blob) {
    removeElementById("visualisation-graph");
    createVisualisationImage(blob);
}

document.addEventListener("DOMContentLoaded", function () {

    //const tooltip = document.querySelector('[data-toggle="tooltip"]').tooltip();

    const getDatabaseButton = document.getElementById("get-database");
    getDatabaseButton.addEventListener('click', async () => {
        const blob = await fetch('http://localhost:1234/database', {
            method: "GET",
        })
            .then(response => response.blob())
            .catch(error => {
                console.error('Error:', error);
            });
        saveFile(blob, "db.json");
    });

    const getEventlogXesButton = document.getElementById("get-eventlog-xes");
    getEventlogXesButton.addEventListener('click', async () => {

        const startDatepicker = document.getElementById("start-date");
        const endDatepicker = document.getElementById("end-date");
        let startDate = startDatepicker.value;
        let endDate = endDatepicker.value;
        console.log(startDate);
        console.log(endDate);

        const dateFilter = {
            'startDate': startDate,
            'endDate': endDate
        }

        const blob = await fetch('http://localhost:1234/xes', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dateFilter)
        })
            .then(response => response.blob())
            .catch(error => {
                console.error('Error:', error);
            });
        saveFile(blob, "eventlog.xes");
    });

    const getImageGetButton = document.getElementById("download-image");
    getImageGetButton.addEventListener('click', async () => {

        const startDatepicker = document.getElementById("start-date");
        const endDatepicker = document.getElementById("end-date");
        let startDate = startDatepicker.value;
        let endDate = endDatepicker.value;
        console.log(startDate);
        console.log(endDate);

        const dateFilter = {
            'startDate': startDate,
            'endDate': endDate
        }

        const blob = await fetch('http://localhost:1234/image', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dateFilter)
        })
        .then(response => response.blob())
        .catch(error => {
            console.error('Error:', error);
        });

        saveFile(blob, "image.png");
    });

    document.getElementById('nav-tab').addEventListener('shown.bs.tab', function (event) {
        
        console.log("ACTIVE TAB");

        // Add your logic here based on the tab change
    });

    const visualisationTab = document.getElementById("nav-visualisation-tab");
    visualisationTab.addEventListener('click', async () => {

        const startDatepicker = document.getElementById("start-date");
        const endDatepicker = document.getElementById("end-date");
        let startDate = startDatepicker.value;
        let endDate = endDatepicker.value;
        console.log(startDate);
        console.log(endDate);

        const dateFilter = {
            'startDate': startDate, // ewentualnie undefined
            'endDate': endDate
        }

        await fetch('http://localhost:1234/image', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dateFilter)
        })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                }
                throw new Error('Something went wrong');
            })
            .then(blob => {
                displayVisualisationImage(blob);
            })
            .catch(error => {
                const errorDiv = document.getElementById("error").style.display = "flex";
                console.error('Error:', error);
            });
    });

    const startDatepicker = document.getElementById("start-date");
    startDatepicker.addEventListener('change', function() {
        let startDate = startDatepicker.value;
        console.log("kurde ", startDate);
    });

    const getEventlogButton = document.getElementById("nav-event-log-tab");
    getEventlogButton.addEventListener('click', async () => {

        // dane z datepickera
        const startDatepicker = document.getElementById("start-date");
        const endDatepicker = document.getElementById("end-date");
        let startDate = startDatepicker.value;
        let endDate = endDatepicker.value;
        console.log(startDate);
        console.log(endDate);

        const dateFilter = {
            'startDate': startDate,
            'endDate': endDate
        }

        await fetch('http://localhost:1234/eventlog', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dateFilter)
        })
            .then(response => response.json())
            .then(data => {
                removeElementById("eventlog-wrapper");

                const visTab = document.getElementById("event-log");
                visTab.style.height = "auto";

                console.log(data);
                let idx = 0;
                const wrapper = document.createElement("div");
                wrapper.setAttribute("id", "eventlog-wrapper");
               

                for (let caseId in data) {
                    //console.log(data[eCase]);
                    const div = document.createElement("div");
                    div.setAttribute("class", "table-responsive");

                    
                    div.innerHTML = "<div>Case ID: " + caseId + "</div>";
                    const table = createTable("table");
                    const tbody = document.createElement("tbody");
                    
                    for (let event of data[caseId]) {
                        //console.log(event);
                        const row = createMainRow(idx);

                        const eventIdCell = document.createElement("td");
                        const fromVisitCell = document.createElement("td");
                        const titleCell = document.createElement("td");
                        //const expandCell = document.createElement("td");
                        //expandCell.setAttribute("class", "expand-button");
                        eventIdCell.textContent = event.eventId;
                        fromVisitCell.textContent = event.fromVisit;
                        titleCell.textContent = event.title;

                        row.appendChild(eventIdCell);
                        row.appendChild(fromVisitCell);
                        row.appendChild(titleCell);
                        //row.appendChild(expandCell);

                        const hideRow = document.createElement("tr");
                        hideRow.setAttribute("class", "hide-table-padding");
                        const tdEmpty = document.createElement("td");
                        hideRow.appendChild(tdEmpty);
                        const td = document.createElement("td");
                        td.setAttribute("colspan", "3");

                        const div1 = createDetailsDiv("Url:", event.url);
                        const div2 = createDetailsDiv("Duration:", getDuration(event.duration));
                        const div3 = createDetailsDiv("Timestamp:", getDateFromTimestamp(event.timestamp));
                        const div4 = createDetailsDiv("Transition:", event.transition);

                        const divCollapse = document.createElement("div");
                        divCollapse.setAttribute("id", "collapse" + idx);
                        divCollapse.setAttribute("class", "collapse in p-3");

                        divCollapse.appendChild(div1);
                        divCollapse.appendChild(div2);
                        divCollapse.appendChild(div3);
                        divCollapse.appendChild(div4);

                        td.appendChild(divCollapse);

                        hideRow.appendChild(td);

                        tbody.appendChild(row);
                        tbody.appendChild(hideRow);
                        idx += 1;
                    }
                    table.appendChild(tbody);
                    div.appendChild(table);
                    div.appendChild(createDivider());
                    wrapper.appendChild(div);
                }
                document.getElementById("eventlog-data").appendChild(wrapper);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});