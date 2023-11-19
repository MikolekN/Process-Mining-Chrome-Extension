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

    const getImageButton = document.getElementById("get-image");
    getImageButton.addEventListener('click', async () => {
        await fetch('http://localhost:1234/image', {
            method: "GET",
        })
            .then(response => response.blob())
            .then(blob => {
                const imgUrl = window.URL.createObjectURL(blob);
                let img = document.createElement('img');
                img.src = imgUrl;
                const container = document.getElementById("zoom");
                container.appendChild(img);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });

    const getEventlogButton = document.getElementById("get-eventlog");
    getEventlogButton.addEventListener('click', async () => {
        await fetch('http://localhost:1234/eventlog', {
            method: "GET",
        })
            .then(response => response.json())
            .then(data => {
                //console.log(data);
                

                for (let caseId in data) {
                    //console.log(data[eCase]);
                    const table = document.createElement("table");
                    table.innerHTML = "<thead><th>Case ID: " + caseId + "</th></thead>";

                    for (let event of data[caseId]) {
                        //console.log(event);
                        table.innerHTML = "<thead><th>event ID</th><th>from visit</th><th>title</th><th>url</th><th>duration</th><th>timestamp</th><th>transition</th></thead>";
                        const row = document.createElement("tr");
                        const eventIdCell = document.createElement("td");
                        const fromVisitCell = document.createElement("td");
                        const titleCell = document.createElement("td");
                        const urlCell = document.createElement("td");
                        const durationCell = document.createElement("td");
                        const timestampCell = document.createElement("td");
                        const transitionCell = document.createElement("td");
                        eventIdCell.textContent = event.eventId;
                        fromVisitCell.textContent = event.fromVisit;
                        titleCell.textContent = event.title;
                        urlCell.textContent = event.url;
                        durationCell.textContent = event.duration;
                        timestampCell.textContent = event.timestamp;
                        transitionCell.textContent = event.transition;
                        row.appendChild(eventIdCell);
                        row.appendChild(fromVisitCell);
                        row.appendChild(titleCell);
                        row.appendChild(urlCell);
                        row.appendChild(durationCell);
                        row.appendChild(timestampCell);
                        row.appendChild(transitionCell);
                        table.appendChild(row);
                    }

                    const eventlogDataContainer = document.getElementById("eventlog-data");
                    eventlogDataContainer.appendChild(table);
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});