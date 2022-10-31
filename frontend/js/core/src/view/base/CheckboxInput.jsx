import {id} from '../../utils.mjs';
import BooleanInput from './BooleanInput.jsx';
import styles from '../base-styles/CheckboxInput.module.css';


/** Base class for all input widgets that could be in two states: true and false.
 * 	Each state is treated as user input and can be changed by the user.
 * 
 * 	The widget can work in parent-controlled and parent-uncontrolled modes.
 * 	In parent-controlled mode the widget state is fully determined by the parent, so
 * 	if parent doesn't change its state, nobody (including the user itself) can't do this.
 * 	Hence, if you want for user to change the state in the parent-controlled-mode,
 * 	you should set the onInputChange callback that modifies the value of corresponding
 * 	props everytime the user change the state of the component.
 * 
 * 	In parent-uncontrolled state child has internal state that defines widget state.
 * 	The parent component can't change the state but the user is free to do this.
 * 
 * 	Props:
 * 		@param {callback} onInputChange		Will be triggered when the user change input state
 * 											Accepts the following data from the user input:
 * 											event.value which is the same to event.target.value - 
 * 												an element state currently set by the user
 * 
 * 		@param {boolean} value 				First, defines the working mode of the widget. If
 * 											the prop exists, the mde is parent-controlled and
 * 											the widget state is fully determined by the value of
 * 											this prop. When the prop is omitted the mode is
 * 											parent-uncontrolled.
 * 
 * 		@param {boolean} defaultValue		Value to be set during the construction of the object.
 * 											defaultValue doesn't affect the working mode of the widget.
 * 
 *      @param {string} error               When the field is valid, do nothing. When the field is not
 *                                          valid, contains a message text that will be shown below the
 *                                          checkbox
 * 
 *      @param {string} label               A short message to be show at the right of the checkbox
 * 
 *      @param {string} tooltip             A long message that will be shown when then user retains mouse
 *                                          pointer near the tooltip.
 * 
 *      @param {boolean} inactive           When equals to true, the user can't change the widget's value by
 *                                          just clicking on it
 * 
 *      @param {boolean} disabled           When equals to true, they widget is marked as grey and the user
 *                                          can't change its value by just clicking on it.
 * 
 * 
 * 	State:
 * 		@param {boolean} value 				Useless in parent-controlled mode. However, in pareent-uncontrolled
 * 											mode it reflects a component state currently set by the user.
 */
 export default class CheckboxInput extends BooleanInput{

    render(){
        let widgetClasses = `${styles.box} checkbox-input`;
        if (this.value){
            widgetClasses += ` ${styles.checked}`;
        }
        if (this.props.disabled){
            widgetClasses += ` ${styles.disabled}`;
        }

        if (this.props.inactive){
            widgetClasses += ` ${styles.inactive}`;
        }

        return (
            <div className={widgetClasses} onClick={this.handleClick} title={this.props.tooltip}>
                <div className={styles.wrapper}>
                    <div className={styles.checkbox}>
                        <svg viewBox="0 0 14 14">
                            <path d="M15-1H-1v16h16V-1zM5 12l-5-5 1.41-1.41L5 9.17l7.59-7.59L14 3l-9 9z"/>
                        </svg>
                    </div>
                    <label>{this.props.label}</label>
                </div>
                { this.props.error && <p className={styles.error_message}>{this.props.error}</p> }
            </div>
        );
    }

 }