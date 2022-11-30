import Button from 'corefacility-base/view/Button';

import styles from './style.module.css';


/** This is a hyperlink. Clicking on this hyperlink results in launching some action.
 * 
 *  Button props:
 *  	@param {string} onClick		a callback that will be invoked when the user clicks the button
 * 		@param {boolean} inactive   if the button is inactive, clicking on it has no effect
 * 		@param {boolean} disabled	if the button is disabled, it is inactive and is shown as grey
 * 		@param {string} href		the route to be moved when you click the button.
 * 	The onClick prop always override the href prop.
 * 
 * 	You can locate any kind of React elements here.
 * 
 * 	*  The component has internal states.
 */
export default class Hyperlink extends Button{

	renderContent(){
		let classList = styles.link_button + " hyperlink" + 
			(this.disabled ? ` ${styles.disabled} disabled` : '') +
			(this.props.inactive ? ` ${styles.inactive}` : '');

		return (<a onClick={this.handleClick} href={this.props.href || '#'}  className={classList}>
			{this.props.children}
		</a>);
	}

}