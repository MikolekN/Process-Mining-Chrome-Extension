let events = [];
let tabToUrl = {};
let prevUrl = undefined, currUrl = undefined;
let prevTabId = undefined, currTabId = undefined;
let prevTabQty = -1, currTabQty = -1;
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
			currTab = currentTab[0];

			currTabInfo = {
				"id": currTab.id,
				"url": currTab.url
			}

			return currTabInfo;
		})
	});

	return currTabInfo;
}

const getVisit = async function(url, idx) {
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
			'text': '',               // return every history item....
			'startTime': oneWeekAgo,  // that was accessed less than one week ago.
			'maxResults': 5000         // state a limit of results
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

	return url.slice(0, 40);
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

const updateEvent = async function(e, lastVisit) {
	
	await updateTitleIfIncorrect(e.title, e.url).then(function(result) {
		e.title = result;
	});
	e.eventId = lastVisit.visitId;
	e.fromVisit = lastVisit.referringVisitId;
	e.transition = lastVisit.transition;
	e.leaveTime = new Date().getTime();
	e.title = replaceSpecialChars(e.title);

	console.log("EWENT: ", e);
	return e;
}

chrome.storage.local.get(['events']).then(async function(result) {
	
	let eventsParsed = JSON.parse(result.events);

	for (let e of eventsParsed) {
		let urlQty = getUrlQtyInEvents(e.url, eventsParsed);
		
		let lastVisit;
		await getVisit(e.url, urlQty).then(function(result) {
			lastVisit = result;
		});
		
		await updateEvent(e, lastVisit).then(function(result) {
			e = result;
		});

		let prevEvent = getEventByUrlAndTabId(e.url, e.tabId, eventsParsed);
		await postEventData(prevEvent);

		eventsParsed = eventsParsed.filter(function (event) {
			return event !== prevEvent;
		});
	}
	chrome.storage.local.remove(['events']);
});

let prevtime = undefined;
let currTime = undefined;


chrome.history.onVisited.addListener(async function(historyItem) {
	
	let currentTab;
	await getCurrentTab().then(function(result) {
		currentTab = result;
	});

	const [loadingTab] = await new Promise(resolve => {
		chrome.tabs.query({
		status: "loading"
	  }, function(loadingTab) {
		resolve(loadingTab);
	})});

	
	const tabs = await new Promise(resolve => {
	chrome.tabs.query({}, function(tabs) {
		resolve(tabs);
	})
	});

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

	prevTabId = currTabId;

	prevTime = currTime;
	currTime = new Date().getTime();

	event_data = {
		"url": currUrl,
		"title": historyItem.title,
		"tabId": currTabId,
		"leaveTime": null,
		"duration": 0,
		"startTime": currTime,
		"endTime": null,
		"tip": false,
		"timestamp": currTime
	}
	events.push(event_data);

	chrome.storage.local.set({ 'events': JSON.stringify(events) });

	let prevEvent = getEventByUrlAndTabId(prevUrl, prevTabId, events);
	if (prevEvent !== undefined && prevEvent.tabId === currTabId) {
		prevEvent.endTime = new Date().getTime();
		prevEvent.duration += prevEvent.endTime - prevEvent.startTime;
	}
});

chrome.tabs.onRemoved.addListener(async function(tabId) {

	let url = tabToUrl[tabId];
	console.log(url, tabId);

	let eventsInRemovedTab = getEventsByTabId(tabId, events);
	console.log(eventsInRemovedTab);
	removing = true;
	for (let [i, e] of eventsInRemovedTab.entries()) {

		let urlQty = getUrlQtyInEvents(e.url, events);
		
		let lastVisit;
		await getVisit(e.url, urlQty).then(function(result) {
			lastVisit = result;
		});
		
		await updateTitleIfIncorrect(e.title, e.url).then(function(result) {
			e.title = result;
		});
		
		await updateEvent(e, lastVisit).then(function(result) {
			e = result;
		});

		if (i === eventsInRemovedTab.length - 1) { 
			if (tabId === currTabId) {
				e.endTime = new Date().getTime();
				e.duration += e.endTime - e.startTime;
			}
		}
		
		let prevEvent = getEventByUrlAndTabId(e.url, e.tabId, events);
		await postEventData(prevEvent);

		events = events.filter(function (event) {
			return event !== prevEvent;
		});
	}

	delete tabToUrl[tabId];

	chrome.storage.local.remove(['events']);
	chrome.storage.local.set({ 'events': JSON.stringify(events) });

	removing = false;
});


chrome.tabs.onActivated.addListener(async function(activeInfo) {

	console.log(currUrl);

	let prevEvent = getEventByUrlAndTabId(currUrl, currTabId, events);
	if (prevEvent !== undefined) {
		prevEvent.endTime = new Date().getTime();
		prevEvent.duration += prevEvent.endTime - prevEvent.startTime;
	}

	prevUrl = currUrl;
	prevTabId = currTabId;

	let currentTab;
	await getCurrentTab().then(function(result) {
		currentTab = result;
	});

	currUrl = currentTab.url;
	currTabId = currentTab.id;

	let currEvent = getEventByUrlAndTabId(currUrl, currTabId, events);
	if (currEvent !== undefined) {
		currEvent.startTime = new Date().getTime();
	}

	let eventsInCurrentTab = getEventsByTabId(currTabId, events);

	if (removing === false) {
		for (let e of eventsInCurrentTab) {

			let urlQty = getUrlQtyInEvents(e.url, events);
			
			let lastVisit;
			await getVisit(e.url, urlQty).then(function(result) {
				lastVisit = result;
			});

			await updateEvent(e, lastVisit).then(function(result) {
				e = result;
			});

			let prevEvent = getEventByUrlAndTabId(e.url, e.tabId, events);
			await postEventData(prevEvent);

			events = events.filter(function (event) {
				return event !== prevEvent;
			});
		}
	}
});

chrome.tabs.onUpdated.addListener(async function(tabId, tab) {
	tabToUrl[tabId] = tab.url;
});
