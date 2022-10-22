import {NotImplementedError} from '../../exceptions/model.mjs';
import CoreWindow from './CoreWindow.jsx';
import HeaderInput from './HeaderInput.jsx';

/** A base class for all window components that represent list of items and
 *  provide the livesearch on such list.
 * 	The window has no props
 * 
 *  Window state:
 * 		@param {string} searchTerm the search phrase entered by the user
 */
export default class LivesearchWindow extends CoreWindow{

	constructor(props){
		super(props);
		this.onSearch = this.onSearch.bind(this);
		this.state = {
			searchTerm: null,
		}
	}

	/** The search placeholder */
	get searchPrompt(){
		throw new NotImplementedError("get searchPrompt");
	}

	/** Updates the window content when the user changes the text in the input box
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	onSearch(event){
		this.setState({searchTerm: event.value});
	}

	/** Renders the livesearch box between the application logo and application controls */
	renderControls(){
		return (<HeaderInput prompt={this.searchPrompt} onInputChange={this.onSearch} defaultValue={this.state.searchTerm}/>);
	}

}
