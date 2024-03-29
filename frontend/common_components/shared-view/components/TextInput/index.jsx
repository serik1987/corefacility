import * as React from 'react';

import Input from 'corefacility-base/view/Input';
import styles from './style.module.css';


/** A special input box suitable for string values
 * 
 *  Props:
 * 		@param {callback} onInputChange		the callback will be executed every time user changes the input
 *                                          the callback function will be invoked with the event argument
 *                                          that contains the 'value' field. This is better to use event.value
 *                                          instead of event.target.value because event.target.value contains
 *                                          row value entered by the user while event.target.value is the value
 *                                          after the following preprocessing:
 *                                           - any whitespaces before and after the value are removed
 *                                           - if the user entered the empty string, the value is null, not ''
 *                                           - you can add additional string preprocessors to this widget
 *                                           - the class descendants may also provide additional preprocessing
 * 
 *      @param {callback} onFocus           Triggers when the input element is in focus
 * 
 *      @param {callback} onBlur            Triggers when the input element loss the focus
 * 
 *      @param {callback} onEnter           Triggers when the user presses the Enter key
 * 
 *		@param {string} value 				Controllable value of the input field. This means that the input value
 *                                          will be set to the value of this prop during each rendering. This results
 *                                          to the following side effects:
 *                                           - If the user entered a value with white spaces, the value is automatically
 *                                             substituted to the value without white spaces.
 *                                           - you obviously need to change the state of the parent component each time
 *                                             the user entered new value. If you will not do this, the component will
 *                                             become useless
 * 
 * 		@param {string} defaultValue		At the first rendering, the input box value will be set to the value
 * 	                                        of this prop. During each next rendering this prop has no effect
 *                                          This prop is overriden by the value prop
 * 
 * 		@param {string} error 				The error message that will be printed when validation fails
 * 
 * 		@param {string} htmlType			Type of the HTML's input element. For list of available types see here:
 * 												https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#input_types
 * 											The following types are supported: email, password, search, tel, text, url
 * 
 * 		@param {string} tooltip				Detailed description of the field
 * 
 *      @param {string} placeholder         The placeholder to output
 * 
 * 		@param {boolean} disabled			When the input box is disabled, it is colored as disabled and the user can't
 * 											enter any value to it
 * 
 * 		@param {boolean} inactive			When the input box is inactive, the user can't enter value to it
 * 
 *      @param {Number} maxLength           Maximum number of symbols in the widget can't exceed this value
 * 
 *      @param {String} cssSuffix           Additional CSS classes to apply
 * 
 * 
 *  The input box has the state 'value' which correspond to the value entered by the user but this is not clear
 *  whether you shall trust on this state value or trust the value of the 'value' prop. So, this is recommended
 *  to use the 'value' property rather than the 'value' state.   
 */
export default class TextInput extends Input{

    constructor(props){
        super(props);
        this.handleKeyPress = this.handleKeyPress.bind(this);

        this.__inputRef = React.createRef();
    }

	get __boxClasses(){
		let boxClasses = `${styles.box} input text-input`;
		if (this.props.disabled){
			boxClasses += ` ${styles.disabled}`;
		}
        if (this.props.cssSuffix){
            boxClasses += ` ${this.props.cssSuffix}`;
        }
		return boxClasses;
	}

    /**
     * Returns the DOM element <input> which is respponsible for posting user's value
     */
    get domInput(){
        return this.__inputRef.current;
    }

    handleKeyPress(event){
        if (event.key === 'Enter' && this.props.onEnter){
            this.props.onEnter(event);
        }
    }

	render(){
		let isError = this.props.error !== "" && this.props.error !== null && this.props.error !== undefined;

		return (
			<div className={this.__boxClasses}>
				<div className={styles.wrapper}>
					<input
						value={this.value}
                        maxLength={this.props.maxLength}
						type={this.props.htmlType}
						title={this.props.tooltip}
                        placeholder={this.props.placeholder}
						disabled={this.props.disabled || this.props.inactive}
						onChange={this.onInputChange}
                        onFocus={this.props.onFocus}
                        onBlur={this.props.onBlur}
                        onKeyPress={this.handleKeyPress}
                        ref={this.__inputRef}
					/>
				</div>
				{ isError && <p className={styles.error}>{this.props.error}</p> }
			</div>
		);
	}

}