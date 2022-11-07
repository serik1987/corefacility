import {NotImplementedError} from '../../exceptions/model.mjs';
import DialogWrapper from './DialogWrapper.jsx';


/** This is the base class for all corefacility windows
 *  Corefacility windows are such components that can define
 *  the title of the Web Browser tab
 *  
 *  The class requires no props.
 */
export default class Window extends DialogWrapper{

	constructor(props){
		super(props);
		this._setBrowserTitle();
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		throw new NotImplementedError("browserTitle");
	}

	/** Sets the browser title from the 'browserTitle' property 
	 * 	@param {string|undefined} title Browser title. Undefined means
	 * 		that browserTitle property will be used.
	 */
	_setBrowserTitle(title){
		let browserTitle = title || this.browserTitle;
		console.log(browserTitle);

		if (browserTitle){
			document.head.getElementsByTagName("title")[0].innerText = browserTitle;
		}
	}

	/*
	shouldComponentUpdate(props, state){
		this._setBrowserTitle();
		return true;
	}
	*/

	componentDidMount(){
		this._setBrowserTitle();
	}

}