import Button from './Button.jsx';
import styles from '../base-styles/Icon.module.css';


/** This is a base class for any button
 *  The button is any widget that executes certain action when
 *  the user clicks on it
 * 
 *  Button props:
 *  	@param {string} onClick		a callback that will be invoked when the user clicks the button
 * 		@param {boolean} inactive   if the button is inactive, clicking on it has no effect
 * 		@param {boolean} disabled	if the button is disabled, it is inactive and is shown as grey
 * 		@param {string} href		the route to be moved when you click the button
 * 		@param {tooltip}			Detailed description of this button
 * 		@param {React.Component} img The image to be displaced to the button.
 * 	The onClick prop always override the href prop
 * 
 *  The component has internal states.
 */
export default class Icon extends Button{


	renderContent(){
		let disabled = this.props.disabled ? ' ' + styles.disabled : '';
		let inactive = this.props.inactive ? ' ' + styles.inactive : '';
		return (
			<a
				onClick={this.handleClick}
				href={this.props.href || '#'}
				className={`${styles.icon_wrapper}${disabled}${inactive} icon`}
				title={this.props.tooltip}>
				<div className={styles.icon}>
					{this.props.src}
				</div>
			</a>
		);
	}
}
