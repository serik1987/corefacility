export default class CustomEvent{

	constructor(eventType, eventOptions){
		this.eventType = eventType;
		this.eventOptions = eventOptions;
	}

}

globalThis.CustomEvent = CustomEvent;