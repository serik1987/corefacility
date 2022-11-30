import Button from 'corefacility-base/view/Button';
import styles from './style.module.css';


/** Colored rectangular button with some HTML structure inside it.
 *  
 *  Button props:
 *      @param {string} type        defines the button design:
 *                                      - 'submit' blue button with white text (by default)
 *                                      - 'more'   white button with blue text; the button becomes gray on hover.
 *                                      - 'cancel' white button with black text, becomes white-shadowed on hover.
 *  	@param {string} onClick		a callback that will be invoked when the user clicks the button
 * 		@param {boolean} inactive   if the button is inactive, clicking on it has no effect
 * 		@param {boolean} disabled	if the button is disabled, it is inactive and is shown as grey
 * 		@param {string} href		the route to be moved when you click the button
 * 	The onClick prop always override the href prop
 * 
 * 	The button label is located as child React elements like here:
 *     <PrimaryButton>Start the Simulation</PrimaryButton>
 * 
 *  The component has internal states.
 */
export default class PrimaryButton extends Button{

	/** Renders the PrimaryButton */
	renderContent(){
        let typeClass = styles[this.props.type];
        if (typeClass === undefined || typeClass === null){
            typeClass = styles.submit;
        }
        let stateClass = this.props.inactive ? ` ${styles.inactive}` : '';

		return (
			<button
                type="button"
                className={"button primary-button " + typeClass + stateClass}
                onClick={this.handleClick}
                disabled={!!this.disabled}>
                {this.props.children}
            </button>
		);
	}
}
