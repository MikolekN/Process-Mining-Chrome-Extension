let events = [];
let startDate = null;
let duration = 0;
let currUrl = undefined;
let prevUrl = undefined;
let currEvent = undefined;
let prevEvent = undefined;
let currTabId = undefined;
let prevTabId = undefined;
let tabToUrl = {};
let currTabQty = -1;
let prevTabQty = -1;
let removing = false;
const weekInMilliseconds = 7*24*60*60*1000; // one week calculated in seconds, maybe some constant for that

const replacements = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
    'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
};


const getCurrentTab = async function() {
	let currTab = undefined;
	let currTabInfo = undefined;

	const [currentTab] = await new Promise(resolve => {
		chrome.tabs.query({ 
			active: true,
			currentWindow: true
		}, function(currentTab) {
			resolve(currentTab);
			//console.log(currentTab);
			currTab = currentTab[0];

			currTabInfo = {
				"id": currTab.id,
				"url": currTab.url
			}

			//console.log(currTabInfo);
			return currTabInfo;
		})
	});

	return currTabInfo;
}

const getVisits = async function(url, idx) {
	const visits = await new Promise(resolve => {
		chrome.history.getVisits({ url: url }, function(visits) {
			resolve(visits);
		});
	});

	return visits.at((-1) * idx);
}

const getHistoryItems = async function() {
	let currentTime = new Date().getTime();
	let oneWeekAgo = currentTime - weekInMilliseconds;

	const historyItems = await new Promise(resolve => {
		chrome.history.search({
			'text': '',               // Return every history item....
			'startTime': oneWeekAgo,  // that was accessed less than one week ago.
			'maxResults': 5000         // Optionally state a limit
		}, 
		function(historyItems) {
			resolve(historyItems);
		});
	});

	return historyItems;
}

const updateTitleIfIncorrect = async function(title, url) {
	if (title === '' || url.includes("youtube")) {
		let historyItems;
		await getHistoryItems().then(function(result) {
			historyItems = result;
		});
		console.log("weszło0");
		return getTitleFromHistoryItemsByUrl(historyItems, url);
	}
	return title;
}

const getTitleFromHistoryItemsByUrl = function(historyItems, url) {
	for (h of historyItems) {
		if (h.url === url) {
			return h.title;
		}
	}

	return url.slice(0, 40); // to chyba nie działa ale jeszcze do sprawdzenia
}

const getUrlQtyInEvents = function(url, events) {
	let urlQty = 0;

	for (e of events) {
		if (e.url === url) {
			urlQty += 1;
		}
	}

	return urlQty;
}

const getEventByUrlAndTabId = function(url, tabId, events) {
	for (let e of events) {
		if (e.url === url && e.tabId === tabId) {
			return e;
		}
	}

	return undefined;
}

const getEventsByTabId = function(tabId, events) {
	eventsInTab = [];

	for (let e of events) {
		if (e.tabId === tabId) {
			eventsInTab.push(e);
		}
	}

	return eventsInTab;
}

const cleanEventData = function(event) {
	delete event['startTime']
	delete event['endTime']
	delete event['tabId'];
	delete event['leaveTime']

	return event;
}

const postEventData = async function(event) {
	let eventToPost = cleanEventData(event);
	console.log(eventToPost); // delete
	await fetch('http://localhost:1234/', {
		method: "POST",
		body: JSON.stringify(eventToPost),
		headers: new Headers({
			"content-type": "application/json"
		})
	});
}

const deleteDuplicates = function(events) {
	if (events.length <= 1) {
		return events;
	}

	const key = 'eventID';
	const arrayUniqueByKey = [...new Map(events.map(event =>
		[event[key], event])).values()];

	return arrayUniqueByKey;
}

const replaceSpecialChars = (str) => {
	return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
								.replace(/[ąćęłńóśźż]/gi, (letter) => replacements[letter]) // Remove accents e.g. polish letters
}

console.log("Background script is running.");
//console.log(events);
chrome.storage.local.get(['events']).then(async function(result) {
	console.log("Value currently is " + result.events);

	let eventsParsed = JSON.parse(result.events);

	console.log(eventsParsed);


	for (const e of eventsParsed) {
		/*const visits = await new Promise(resolve => {
			chrome.history.getVisits({ url: e.url }, function(visits) {
				resolve(visits);
			});
		});*/

		let urlQty = getUrlQtyInEvents(e.url, eventsParsed);
		
		let lastVisit;
		await getVisits(e.url, urlQty).then(function(result) {
			lastVisit = result;
		});

		//console.log(visits);
		//console.log(events);

		//lastVisit = visits.at((-1) * urlQty); 

		//console.log("TITLE: ")
		
		await updateTitleIfIncorrect(e.title, e.url).then(function(result) {
			e.title = result;
		});
		
		e.eventId = lastVisit.visitId;
		//e.isLocal = lastVisit.isLocal;
		e.fromVisit = lastVisit.referringVisitId;
		e.transition = lastVisit.transition;
		//e.timestamp = lastVisit.visitTime
		e.leaveTime = new Date().getTime();
		e.title = replaceSpecialChars(e.title);

		let prevEvent = getEventByUrlAndTabId(e.url, e.tabId, eventsParsed);
		console.log(prevEvent);
		await postEventData(prevEvent);

		eventsParsed = eventsParsed.filter(function (event) {
			return event !== prevEvent;
		});
	}
	chrome.storage.local.remove(['events']);
});

//chrome.storage.local.get(['events']).then((result) => {
//	console.log("Value currently is " + result.events);
//});

let prevtime = undefined;
let currTime = undefined;


chrome.history.onVisited.addListener(async function(historyItem) {
	
	let currentTab;
	await getCurrentTab().then(function(result) {
		currentTab = result;
	});

	const [loadingTab] = await new Promise(resolve => {
		chrome.tabs.query({ // na razie zostawie takie coś ale wcześniej było active itd
		// dla tej wartosci a nie active jest dobre id dla otwartej w nowej karcie
		status: "loading"
	  }, function(loadingTab) {
		resolve(loadingTab);
	  })});

	console.log("CURR TAb", currentTab);
	
	const tabs = await new Promise(resolve => {
	chrome.tabs.query({}, function(tabs) {
		resolve(tabs);
	})
	});
	//console.log('Number of open tabs ', tabs.length);
	prevTabQty = currTabQty;
	currTabQty = tabs.length;

	if (currTabQty > prevTabQty) {
		prevUrl = undefined;
		currUrl = historyItem.url;
		if (loadingTab !== undefined) {
			currTabId = loadingTab.id;
		}
		else {
			currTabId = currentTab.id;
		}
	}
	else {
		prevUrl = currUrl;
		currUrl = historyItem.url;
		currTabId = currentTab.id;
	}

	// trzeba dodac przesuwanie tabId dla current też, ale to wystarczy skopiować z kodu niżej
	prevTabId = currTabId;
	//currTabId = currentTab.id;
	console.log(currTabId);

	prevTime = currTime;
	currTime = new Date().getTime();

	if (Math.abs(currTime - prevTime) > 1000) { // większy niż 1 sek, ten czas do ustalenia jeszcze
		console.log("GG");
	}

	event_data = {
		"url": currUrl,
		"title": historyItem.title, // moze bedzie mozliwosc usuniecia
		"tabId": currTabId,
		"leaveTime": null,
		"duration": 0,
		"startTime": currTime,
		"endTime": null,
		"tip": false,
		"timestamp": currTime
	}
	events.push(event_data);

	//
	//
		// popracować nad błędem: Uncaught (in promise) SyntaxError: "undefined" is not valid JSON związanym z
		// listą events
	//
	//

	chrome.storage.local.set({ 'events': JSON.stringify(events) }).then(() => {
		console.log("Value is set");
	});

	chrome.storage.local.get(['events']).then((result) => {
		console.log("Value currently is " + result.events);
	});
	//localStorage.setItem("events", JSON.stringify(events));

	console.log("EVENTS LIST = ", events);

	console.log("V -> ", prevUrl, " ", currUrl);


	let prevEvent = getEventByUrlAndTabId(prevUrl, prevTabId, events);
	if (prevEvent !== undefined && prevEvent.tabId === currTabId) { // było prevEvent.tabId
		prevEvent.endTime = new Date().getTime();
		prevEvent.duration += prevEvent.endTime - prevEvent.startTime;
	}
});

chrome.tabs.onRemoved.addListener(async function(tabId) {

	// nie wiem czy zostawać przy tej tablicy, bo moglbym szukac ostatniego url w events ktory ma tabId
	let url = tabToUrl[tabId];
	console.log(url, tabId);

	let eventsInRemovedTab = getEventsByTabId(tabId, events);
	console.log(eventsInRemovedTab);
	removing = true;
	for (const [i, e] of eventsInRemovedTab.entries()) {
		/*const visits = await new Promise(resolve => {
			chrome.history.getVisits({ url: e.url }, function(visits) {
				resolve(visits);
			});
		});*/

		let urlQty = getUrlQtyInEvents(e.url, events);
		
		let lastVisit;
		await getVisits(e.url, urlQty).then(function(result) {
			lastVisit = result;
		});

		//console.log(visits);
		console.log(events);

		//lastVisit = visits.at((-1) * urlQty); 

		//console.log("TITLE: ")
		
		await updateTitleIfIncorrect(e.title, e.url).then(function(result) {
			e.title = result;
		});
		
		e.eventId = lastVisit.visitId;
		//e.isLocal = lastVisit.isLocal;
		e.fromVisit = lastVisit.referringVisitId;
		e.transition = lastVisit.transition;
		//e.timestamp = lastVisit.visitTime
		e.leaveTime = new Date().getTime();
		
		if (i === eventsInRemovedTab.length - 1) { 
			if (tabId === currTabId) {
				e.endTime = new Date().getTime();
				e.duration += e.endTime - e.startTime;
			}
		}
		e.title = replaceSpecialChars(e.title);
		let prevEvent = getEventByUrlAndTabId(e.url, e.tabId, events);
		console.log(prevEvent);
		await postEventData(prevEvent);

		events = events.filter(function (event) {
			return event !== prevEvent;
		});
	}

	// Remove information for non-existent tab
	delete tabToUrl[tabId];

	console.log(events);
	chrome.storage.local.remove(['events']);
	chrome.storage.local.set({ 'events': JSON.stringify(events) }).then(() => {
		console.log("Value is set");
	});

	console.log("R -> ", prevUrl, " ", currUrl);
	removing = false;
});


chrome.tabs.onActivated.addListener(async function(activeInfo) {

	console.log(currUrl);

	let prevEvent = getEventByUrlAndTabId(currUrl, currTabId, events);
	if (prevEvent !== undefined) {
		prevEvent.endTime = new Date().getTime();
		prevEvent.duration += prevEvent.endTime - prevEvent.startTime;
		console.log("pe -> ", prevEvent);
	}

	prevUrl = currUrl;
	prevTabId = currTabId;

	let currentTab;
	await getCurrentTab().then(function(result) {
		currentTab = result;
	});

	currUrl = currentTab.url;
	currTabId = currentTab.id;

	//console.log(currUrl, currTabId);

	let currEvent = getEventByUrlAndTabId(currUrl, currTabId, events);
	if (currEvent !== undefined) {
		currEvent.startTime = new Date().getTime();
		console.log("ce -> ", currEvent);
	}

	console.log("A -> ", prevUrl, " ", currUrl);

	// currentTab in this moment indicates previous active tab
	let eventsInCurrentTab = getEventsByTabId(currTabId, events);
	let lastEventInCurrentTab = eventsInCurrentTab.pop(); // dla RM bez tego, bo chce wyslac wszystko co w danej karcie
	console.log(eventsInCurrentTab); // wszystkie bez ostatniego eventu
	console.log(lastEventInCurrentTab); // ostatni event

	if (removing === false) {
		for (let e of eventsInCurrentTab) {
			/*const visits = await new Promise(resolve => {
			chrome.history.getVisits({ url: e.url }, function(visits) {
				resolve(visits);
			});
			});*/

			//console.log("VISITS: ", visits);

			// pomysł jest taki ze jesli refId == 0 to zostawiam na ostatnim, jesli nie to szukam w visits
			// elementu ktory ma refId na poprzedni eventId/visitId
			// albo tą część przenieść do onvisited ale pewnie tam cos znowu by sie wysypało
			// jeszcze inny pomysł bo tutaj chodzi o to, że kilka razy pojawia się ten sam url
			// i ja biore po prostu ostatni, moze policzyc ile jest tych samych i cofnąć od konca listy visits
			// np. url == "https://enauczanie.pg.edu.pl/moodle/login/index.php?authCAS=CAS" jest 3 razy => times
			// no to wtedy visits.at( (-times) )
			// i moze zawsze brać liczba wystąpien od konca ale to też trzebaby przesuwać albo liczyś każdorazowo i 
			// usuwać z listy po wysłaniu z listy events

			//console.log(events);
			let urlQty = getUrlQtyInEvents(e.url, events);
			
			let lastVisit;
			await getVisits(e.url, urlQty).then(function(result) {
				lastVisit = result;
			});

			//lastVisit = visits.at((-1) * urlQty); 



			//let currentTime = new Date().getTime();
			//let oneWeekAgo = currentTime - weekInMilliseconds;

			// to wywołanie moze w ogole dac do funkcji getTitleFromHistoryItemsByUrl 
			// bo tylko wtedy jest potrzebne
			
			//console.log("HIST_ITEMS = ", historyItems);
			//let visitedHistoryItem = historyItems.at(0); // first found
			//console.log("visited HI == ", visitedHistoryItem);


			//console.log("TITLE: ")
			await updateTitleIfIncorrect(e.title, e.url).then(function(result) {
				e.title = result;
			});
			e.eventId = lastVisit.visitId;
			
			//e.isLocal = lastVisit.isLocal;
			
			e.fromVisit = lastVisit.referringVisitId;
			e.transition = lastVisit.transition;
			//
			// wyzej przy onvisited biore tytul jak nie to mozna przeszukać histItems po url
			// dla YouTube trzeba zrobić szukanie po histItems i można też przetestować dla wszystkich czy to
			// się opłaci czasowo
			//
			// przekopiować logikę wysyłania z poprzedniej wersji bo tam też miałem sumowanie pod duration
			// dodatkowo trzeba popracować nad duration
			//e.title = visitedHistoryItem.title;
			
			//e.timestamp = lastVisit.visitTime;

			// to liczenie duration powinienem mieć chyba tak jak wcześniej w on visited
			// tam będzie sie sumować a na onActivated lub removed dodatkowe doliczenie

			//e.endTime = new Date().getTime();
			//e.duration += e.endTime - e.startTime;
			e.title = replaceSpecialChars(e.title);
			let prevEvent = getEventByUrlAndTabId(e.url, e.tabId, events);
			await postEventData(prevEvent);

			// trzeba dopracowac wysylanie na evencie on removed
			// sprawdzic czy działa doliczanie czasu w activated i removed

			events = events.filter(function (event) {
				return event !== prevEvent;
			});

			//console.log(events);
		}
	}
	let eventsInCurrentTab2 = getEventsByTabId(currTabId, events);
	console.log(eventsInCurrentTab2);
});

chrome.tabs.onUpdated.addListener(async function(tabId, tab) {
	tabToUrl[tabId] = tab.url;
	console.log("U -> ", prevUrl, " ", currUrl);
});

chrome.windows.onRemoved.addListener(async function(windowId) {
	console.log("WINDOW REMOVED ", windowId);

	const tabs = await new Promise(resolve => {
		chrome.tabs.query({
		windowId: windowId
	}, function(tabs) {
		resolve(tabs);
	})});
	console.log(tabs);
	console.log(events);


	// to nie dziala
	//for (let e of events) {
	//	postEventData(e);
	//}
})
