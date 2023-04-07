import Button from 'corefacility-base/view/Button';

import styles from './style.module.css';


/** This is a base class for any button
 *  The button is any widget that executes certain action when
 *  the user clicks on it
 * 
 *  Button props:
 * 	--------------------------------------------------------------------------------------------------------------------
 *  @param {string}				onClick		a callback that will be invoked when the user clicks the button
 * 	@param {string} 			type 		icon type: 'default', 'mini'
 * 	@param {boolean}			inactive	if the button is inactive, clicking on it has no effect
 * 	@param {boolean}			disabled	if the button is disabled, it is inactive and is shown as grey
 * 	@param {string}				href		the route to be moved when you click the button, given that onClick prop
 * 											has not been specified
 * 	@param {string}				tooltip		Detailed description of this button
 * 	@param {React.Component} 	src 		The image to be displaced to the button.
 * 	@param {string}				cssSuffix 	Additional CSS styles to apply
 * 
 *  The icon component is fully stateless
 */
export default class Icon extends Button{


	renderContent(){
		let disabled = this.disabled ? ' ' + styles.disabled : '';
		let inactive = this.props.inactive ? ' ' + styles.inactive : '';
		let cssSuffix = this.props.cssSuffix ? ` ${this.props.cssSuffix}` : '';

		let iconClasses = `${styles.icon_wrapper}${disabled}${inactive}${cssSuffix} icon`;
		if (this.props.type && this.props.type in styles){
			iconClasses += ` ${styles[this.props.type]}`;
		}

		return (
			<a
				onClick={this.handleClick}
				href={this.props.href || '#'}
				className={iconClasses}
				title={this.props.tooltip}>
				<div className={styles.icon}>
					{this.props.src}
				</div>
			</a>
		);
	}
}
