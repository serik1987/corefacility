import {jest} from "@jest/globals";
import CustomEvent from './custom-event.mjs';

class Document{

	constructor(){
		this.dispatchEvent = jest.fn(event => {
			expect(event).toBeInstanceOf(CustomEvent);
		});
	}

}

globalThis.document = new Document();
export default Document;