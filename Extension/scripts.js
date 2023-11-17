document.addEventListener("DOMContentLoaded", function () {
    // const getChromeHistoryButton = document.getElementById("getChromeHistory");
    // getChromeHistoryButton.addEventListener('click', async function() {
    //     let i = []

    //     const historyItems = await new Promise(resolve => {
    //         chrome.history.search({ text: '', startTime: 0 }, function(historyItems) {
    //             resolve(historyItems);
    //         });
    //     });

    //     for (const item of historyItems) {
    //         const visits = await new Promise(resolve => {
    //             chrome.history.getVisits({ url: item.url }, function(visits) {
    //                 resolve(visits);
    //             });
    //         });

    //         visits.forEach((visit) => {
    //             //console.log(item.title + " - " + visit.visitTime);
    //             data = {}
    //             data['visit_id'] = visit.visitId
    //             data['isLocal'] = visit.isLocal
    //             data['fromVisit'] = visit.referringVisitId
    //             data['transition'] = visit.transition
    //             data['visitTime'] = visit.visitTime
    //             data['title'] = item.title
    //             data['url'] = item.url
    //             i.push(data);
    //         });
    //     }
        
    //     console.log(i)
    // })

    const getDatabaseButton = document.getElementById("get-database");
    getDatabaseButton.addEventListener('click', async () => {
        fetch('http://localhost:1234/database', {
            method: "GET",
        })
            .then(response => response.blob())
            .then(blob => {
                let url = window.URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = "history_db.json";
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });

    const getEventlogXesButton = document.getElementById("get-eventlog-xes");
    getEventlogXesButton.addEventListener('click', async () => {
        fetch('http://localhost:1234/xes', {
            method: "GET",
        })
            .then(response => response.blob())
            .then(blob => {
                let url = window.URL.createObjectURL(blob);
                let a = document.createElement('a');
                a.href = url;
                a.download = "eventlog.xes";
                document.body.appendChild(a);
                a.click();
                a.remove();
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });

    const getImageButton = document.getElementById("get-image");
    getImageButton.addEventListener('click', async () => {
        fetch('http://localhost:1234/image', {
            method: "GET",
        })
            .then(response => response.blob())
            .then(blob => {
                const imgUrl = window.URL.createObjectURL(blob);
                let img = document.createElement('img');
                img.src = imgUrl;
                const container = document.getElementById("test-img-endpoint");
                container.appendChild(img);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });

    const getEventlogButton = document.getElementById("get-eventlog");
    getEventlogButton.addEventListener('click', async () => {
        fetch('http://localhost:1234/eventlog', {
            method: "GET",
        })
            .then(response => response.text())
            .then(data => {
                console.log(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
    });
});