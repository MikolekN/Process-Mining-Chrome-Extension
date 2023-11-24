const createTableTh = function(content) {
    const th = document.createElement("th");
    th.setAttribute("scope", "col");
    th.textContent = content;

    return th;
}

const createTable = function(className) {
    const table = document.createElement("table");
    table.setAttribute("class", className);
    const thead = document.createElement("thead");
    const tr = document.createElement("tr");
    
    const th1 = createTableTh("Event ID");
    const th2 = createTableTh("Ref Event ID");
    const th3 = createTableTh("Title");
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

document.addEventListener("DOMContentLoaded", function () {
    
    const saveFile = async (blob, suggestedName) => {
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
        // Create the `` element and append it invisibly.
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
        const blob = await fetch('http://localhost:1234/xes', {
            method: "GET",
        })
            .then(response => response.blob())
            .catch(error => {
                console.error('Error:', error);
            });
        saveFile(blob, "eventlog.xes");
    });

    const getImageGetButton = document.getElementById("download-image");
    getImageGetButton.addEventListener('click', async () => {
        const blob = await fetch('http://localhost:1234/image', {
            method: "GET",
        })
            .then(response => response.blob())
            .catch(error => {
                console.error('Error:', error);
            });
        saveFile(blob, "image.png");
    });

    const getImageUpdateButton = document.getElementById("update-image");
    getImageUpdateButton.addEventListener('click', async () => {
        await fetch('http://localhost:1234/image', {
            method: "GET",
        })
            .then(response => {
                if (response.ok) {
                    return response.blob();
                }
                throw new Error('Something went wrong');
            })
            .then(blob => {
                if (document.contains(document.getElementById("visualisation-graph"))) {
                    document.getElementById("visualisation-graph").remove();
                }
                const imgUrl = window.URL.createObjectURL(blob);
                let img = document.createElement('img');
                img.setAttribute("id", "visualisation-graph");
                img.src = imgUrl;
                const container = document.getElementById("zoom");
                container.appendChild(img);
            })
            .catch(error => {
                const errorDiv = document.getElementById("error").style.display = "flex";
                console.error('Error:', error);
            });
    });

    const getEventlogButton = document.getElementById("get-eventlog");
    getEventlogButton.addEventListener('click', async () => {

        // dane z datepickera
        const startDatepicker = document.getElementById("start-date");
        const endDatepicker = document.getElementById("end-date");
        var startDate = startDatepicker.value;
        var endDate = endDatepicker.value;
        console.log(startDate);
        console.log(endDate);

        await fetch('http://localhost:1234/eventlog', {
            method: "GET",
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                let idx = 0;
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

                        let duration = event.duration / 1000;
                        let durationContent = duration.toString() + " s";

                        var a = new Date(event.timestamp);
                        var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
                        var year = a.getFullYear();
                        var month = months[a.getMonth()];
                        var date = a.getDate();
                        var hour = a.getHours();
                        if (hour < 10) {
                            hour = "0" + hour.toString();
                        }
                        var min = a.getMinutes();
                        if (min < 10) {
                            min = "0" + min.toString();
                        }
                        var sec = a.getSeconds();
                        if (sec < 10) {
                            sec = "0" + sec.toString();
                        }
                        var timestampContent = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;

                        const div1 = createDetailsDiv("Url:", event.url);
                        const div2 = createDetailsDiv("Duration:", durationContent);
                        const div3 = createDetailsDiv("Timestamp:", timestampContent);
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
                    const eventlogDataContainer = document.getElementById("eventlog-data");
                    eventlogDataContainer.appendChild(div);
                }

                // for (let caseId in data) {
                //     //console.log(data[eCase]);
                //     const div = document.createElement("div");
                //     div.innerHTML = "<div>Case ID: " + caseId + "</div>";
                //     const table = createTable();

                //     for (let event of data[caseId]) {
                //         //console.log(event);
                //         const row = document.createElement("tr");
                //         const eventIdCell = document.createElement("td");
                //         const fromVisitCell = document.createElement("td");
                //         const titleCell = document.createElement("td");
                //         const urlCell = document.createElement("td");
                //         const durationCell = document.createElement("td");
                //         const timestampCell = document.createElement("td");
                //         const transitionCell = document.createElement("td");
                //         eventIdCell.textContent = event.eventId;
                //         fromVisitCell.textContent = event.fromVisit;
                //         titleCell.textContent = event.title;
                //         urlCell.textContent = event.url;
                //         durationCell.textContent = event.duration;
                //         timestampCell.textContent = event.timestamp;
                //         transitionCell.textContent = event.transition;
                //         row.appendChild(eventIdCell);
                //         row.appendChild(fromVisitCell);
                //         row.appendChild(titleCell);
                //         row.appendChild(urlCell);
                //         row.appendChild(durationCell);
                //         row.appendChild(timestampCell);
                //         row.appendChild(transitionCell);
                //         table.appendChild(row);
                //     }
                //     div.appendChild(table);
                //     const eventlogDataContainer = document.getElementById("eventlog-data");
                //     eventlogDataContainer.appendChild(div);
                // }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});