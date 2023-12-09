let startDate = undefined, endDate = undefined;

const saveFile = async function(blob, suggestedName) {
    const supportsFileSystemAccess =
        'showSaveFilePicker' in window &&
        (() => {
            try {
                return window.self === window.top;
            } catch {
                return false;
            }
        })();
    if (supportsFileSystemAccess) {
        try {
            const handle = await showSaveFilePicker({
                suggestedName,
            });
            const writable = await handle.createWritable();
            await writable.write(blob);
            await writable.close();
            return;
        } catch (err) {
            if (err.name !== 'AbortError') {
                console.error(err.name, err.message);
                return;
            }
        }
    }
    const blobURL = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobURL;
    a.download = suggestedName;
    a.style.display = 'none';
    document.body.append(a);
    a.click();
    setTimeout(() => {
        URL.revokeObjectURL(blobURL);
        a.remove();
    }, 1000);
};

const getVisualisation = async function() {
    removeElementById("visualisation-graph");
    const dateFilter = {
        'startDate': startDate,
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
        document.getElementById("visualisation-error").style.display = "none";
        displayVisualisationImage(blob);
    })
    .catch(error => {
        document.getElementById("visualisation-error").style.display = "flex";
        console.error('Error:', error);
    });
}

const getEventLogData = async function() {
    
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

            let idx = 0;
            const wrapper = document.createElement("div");
            wrapper.setAttribute("id", "eventlog-wrapper");
           
            for (let caseId in data) {
                const card = document.createElement("div");
                card.setAttribute("class", "table-responsive card eventlog-table");

                const header = document.createElement("div");
                header.setAttribute("class", "card-header");
                header.textContent = "Case ID: " + caseId;
                card.appendChild(header);
                const content = document.createElement("div");
                content.setAttribute("class", "card-content");
                const table = createTable("table");
                const tbody = document.createElement("tbody");
                
                for (let event of data[caseId]) {
                    const row = createAccordionElement("tr", idx);

                    const eventIdCell = document.createElement("td");
                    const fromVisitCell = document.createElement("td");
                    const titleCell = document.createElement("td");
                    eventIdCell.textContent = event.eventId;
                    fromVisitCell.textContent = event.fromVisit;
                    titleCell.textContent = event.title;

                    row.appendChild(eventIdCell);
                    row.appendChild(fromVisitCell);
                    row.appendChild(titleCell);

                    const hideRow = document.createElement("tr");
                    hideRow.setAttribute("class", "hide-table-padding");
                    const td = document.createElement("td");
                    td.setAttribute("colspan", "3");

                    const div1 = createDetailsDiv("Url:", event.url);
                    const div2 = createDetailsDiv("Duration:", getDuration(event.duration));
                    const div3 = createDetailsDiv("Timestamp:", getDateFromTimestamp(event.timestamp));
                    const div4 = createDetailsDiv("Transition:", event.transition);

                    const divCollapse = document.createElement("div");
                    divCollapse.setAttribute("id", "collapse" + idx);
                    divCollapse.setAttribute("class", "collapse in p-3 border border-primary rounded");

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
                content.appendChild(table);
                card.appendChild(content);
                wrapper.appendChild(card);
            }
            document.getElementById("eventlog-data").appendChild(wrapper);
        })
        .catch(error => {
            document.getElementById("eventlog-error").style.display = "flex";
            console.error('Error:', error);
        });
}

const getEventsData = async function() {

    const dateFilter = {
        "startDate": startDate,
        "endDate": endDate
    }

    await fetch('http://localhost:1234/', {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dateFilter)
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Something went wrong');
        })
        .then(data => {
            console.log(data);

            removeElementById("events-wrapper");

            const visTab = document.getElementById("events");
            visTab.style.height = "auto";

            console.log(data);
            let idx = 0;
            const wrapper = document.createElement("div");
            wrapper.setAttribute("id", "events-wrapper");
        
            for (let i in data) {
                const event = data[i];
                console.log(event);

                const card = document.createElement("div");
                card.setAttribute("class", "card events-card");
                const header = createAccordionElement("div", idx);
                header.setAttribute("class", "accordion-toggle collapsed card-header");
                header.innerHTML = "<b>Visit at: </b>" + event.title;
                card.appendChild(header);
                const content = document.createElement("div");
                content.setAttribute("class", "card-content");

                const div1 = createDetailsDiv("Url:", event.url);
                const div2 = createDetailsDiv("Duration:", getDuration(event.duration));
                const div3 = createDetailsDiv("Timestamp:", getDateFromTimestamp(event.timestamp));
                const div4 = createDetailsDiv("Transition:", event.transition);

                const divCollapse = document.createElement("div");
                divCollapse.setAttribute("id", "collapse" + idx);
                divCollapse.setAttribute("class", "collapse in p-3 border border-primary rounded");

                divCollapse.appendChild(div1);
                divCollapse.appendChild(div2);
                divCollapse.appendChild(div3);
                divCollapse.appendChild(div4);

                content.appendChild(divCollapse);

                card.appendChild(content);
                wrapper.appendChild(card);

                idx += 1;
            }
            document.getElementById("events-data").appendChild(wrapper);
        })
        .catch(error => {
            const errorDiv = document.getElementById("events-error").style.display = "flex";
            console.error('Error:', error);
        });
}

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

    tr.appendChild(th1);
    tr.appendChild(th2);
    tr.appendChild(th3);
    thead.appendChild(tr);
    table.appendChild(thead);

    return table;
}

const createAccordionElement = function(element, idx) {
    const row = document.createElement(element);
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
    div1.setAttribute("class", "col");
    div1.innerHTML = "<b>" + label + "</b> " + content;
    const div3 = document.createElement("div");
    div3.setAttribute("class", "row");
    div3.appendChild(div1);

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

    let date = formatDateElement(eventDate.getDate());
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

const getCurrentDate = function() {
    let date = new Date();
    let year = date.getFullYear();
    let month = formatDateElement(date.getMonth() + 1);
    let day = formatDateElement(date.getDate());
    
    return [year, month, day].join('-');
}

const setCurrentDate = function() {
    let date = getCurrentDate();
    
    document.getElementById("start-date").value = date;
    document.getElementById("end-date").value = date;
}

document.addEventListener("DOMContentLoaded", function () {

    setCurrentDate();
    getVisualisation();

    const filterToggle = document.getElementById("filter-toggle");
    filterToggle.addEventListener('click', function() {
        if (filterToggle.getAttribute("aria-expanded") === "true") {
            startDate = document.getElementById("start-date").value;
            endDate = document.getElementById("end-date").value;
            console.log(startDate, endDate);
        }
        else if (filterToggle.getAttribute("aria-expanded") === "false") {
            startDate = undefined;
            endDate = undefined;
        }
    });

    const resetFilterButton = document.getElementById("reset-filter");
    resetFilterButton.addEventListener('click', function() {
        startDate = undefined;
        endDate = undefined;

        document.getElementById("start-date").value = "";
        document.getElementById("end-date").value = "";

        getEventLogData();
    });

    const getDatabaseButton = document.getElementById("get-database");
    getDatabaseButton.addEventListener('click', async () => {
        await fetch('http://localhost:1234/database', {
            method: "GET",
        })
        .then(async response => {
            const blob = await response.blob()
            saveFile(blob, "db.json");
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    const getEventlogXesButton = document.getElementById("get-eventlog-xes");
    getEventlogXesButton.addEventListener('click', async () => {

        const dateFilter = {
            'startDate': startDate,
            'endDate': endDate
        }

        await fetch('http://localhost:1234/xes', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dateFilter)
        })
        .then(async response => {
            const blob = await response.blob();
            saveFile(blob, "eventlog.xes");
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    const getImageGetButton = document.getElementById("download-image");
    getImageGetButton.addEventListener('click', async () => {

        const dateFilter = {
            'startDate': startDate,
            'endDate': endDate
        }

        await fetch('http://localhost:1234/image', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dateFilter)
        })
        .then(async response => {
            const blob = await response.blob();
            saveFile(blob, "image.png");
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

    const visualisationTab = document.getElementById("nav-visualisation-tab");
    visualisationTab.addEventListener('click', async () => {
        getVisualisation();
    });

    const visualisationButton = document.getElementById("refresh-visualisation");
    visualisationButton.addEventListener('click', async () => {
        getVisualisation();
    });

    const filterButton = document.getElementById("filter-data");
    filterButton.addEventListener('click', function() {
        const activeTab = document.querySelector("button.active");

        if (activeTab.textContent.trim() === "Event Log") {
            getEventLogData();
        }
        else if (activeTab.textContent.trim() === "Visualisation") {
            getVisualisation();
        }
        else if (activeTab.textContent.trim() === "Events") {
            getEventsData();
        }
    });

    const startDatepicker = document.getElementById("start-date");
    startDatepicker.addEventListener('change', function() {
        startDate = document.getElementById("start-date").value;
        if (startDate === "") {
            startDate = undefined;
        }
        console.log("start date: ", startDate);
    });

    const endDatepicker = document.getElementById("end-date");
    endDatepicker.addEventListener('change', function() {
        endDate = document.getElementById("end-date").value;
        if (endDate === "") {
            endDate = undefined;
        }
        console.log("end date: ", endDate);
    });

    const getEventlogTab = document.getElementById("nav-event-log-tab");
    getEventlogTab.addEventListener('click', async () => {
        getEventLogData();
    });

    const getEventlogButton = document.getElementById("get-eventlog");
    getEventlogButton.addEventListener('click', async () => {
        getEventLogData();
    })

    const getEventlogListButton = document.getElementById("get-events");
    getEventlogListButton.addEventListener('click', async function() {
        getEventsData();
    });

    const getEventlogListTab = document.getElementById("nav-events-tab");
    getEventlogListTab.addEventListener('click', async function() {
        getEventsData();
    });
});