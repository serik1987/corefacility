import Button from './Button.jsx';


/** This is the base class for all list items (i.e., children of the ItemList component)
 * 
 *  Props:
 *  	@param {string} onClick		a callback that will be invoked when the user clicks the button
 * 										data of the event passed to the callback has event.detail
 * 										property equal to a certain item attached to the list
 * 	WARNING: when you render this component within an instance of ItemList, you always must set
 *  this property to this.onItemSelect to lift up the state
 * 		@param {boolean} inactive   if the button is inactive, clicking on it has no effect
 * 		@param {boolean} disabled	if the button is disabled, it is inactive and is shown as grey 
 * 		@param {Entity} item 		The item attached to the list
 * 	Please note that href property is not implemented here.
 */
export default class ListItem extends Button{

	/**
	 *  handles the button click.
	 *  When you will decide to extend this base class, pass exactly this callback
	 *  to the callback props, because it accounts for disabled and inactive props
	 */
	handleClick(event){

		if (!this.props.inactive && !this.props.disabled){
			if (this.props.item){
				event.detail = this.props.item;
			} else {
				event.detail = null;
			}
			if (this.props.onClick){
				this.props.onClick(event);
			}
		}
	}

}