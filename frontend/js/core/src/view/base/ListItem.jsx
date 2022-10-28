import Button from './Button.jsx';
import ItemList from './ItemList.jsx';


/** This is the base class for all list items (i.e., children of the ItemList component)
 * 
 *  Props:
 *  	@param {string} onClick		a callback that will be invoked when the user clicks the button
 * 										data of the event passed to the callback has event.detail
 * 										property equal to a certain item attached to the list
 * 	WARNING: when you render this component within an instance of ItemList, you can set
 *  this property to this.onItemSelect to lift up the state
 * 		@param {boolean} inactive   if the button is inactive, clicking on it has no effect
 * 		@param {boolean} disabled	if the button is disabled, it is inactive and is shown as grey 
 * 		@param {Entity} item 		The item attached to the list
 * 		@param {string} href		the route to be moved when you click the button
 */
export default class ListItem extends Button{

	constructor(props){
		super(props);
	}

	/** This function calls after creating the ListItem for entity tagged by 'recentlyAdded'.
	 * 
	 * 	You can leave this function empty or put your own developed animation here.
	 */
	itemAddAnimationStart(){}

	/**
	 *  handles the button click.
	 *  When you will decide to extend this base class, pass exactly this callback
	 *  to the callback props, because it accounts for disabled and inactive props
	 */
	handleClick(event){
		if (this.props.item){
			event.detail = this.props.item;
		} else {
			event.detail = null;
		}
		super.handleClick(event);
	}

	componentDidMount(){
		if (this.props.item.tag === "recentlyAdded"){
			this.itemAddAnimationStart();
			this.props.item.tag = undefined;
		}
	}

}