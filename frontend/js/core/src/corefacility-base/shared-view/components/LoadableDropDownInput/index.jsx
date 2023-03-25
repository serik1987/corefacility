import DropDownInput from 'corefacility-base/view/DropDownInput';

import styles from './style.module.css';


/** A special kind of drop-down input where dropping content is list of items, each of which is clickable. The list
 *  itself is suggested to be rendered by the parent widget, not the superclass.
 * 
 *  Props:
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {boolean} inactive           if true, the input box will be inactive and hence will not expand or contract
 *                                      the item box.
 * 
 *  @param {boolean} disabled           When the input box is disabled, it is colored as disabled and the user can't
 *                                      enter any value to it
 * 
 *  @param {string} error               The error message that will be printed when validation fails
 * 
 *  @param {string} tooltip             Detailed description of the field
 * 
 *  @param {string} placeholder         The input placeholder
 * 
 *  @param {callback} onInputChange     Triggers when the user changes the input
 * 
 *  @param {React.Component} children   The <ul> item to show when the user opens the drop down.
 * 
 *  @param {callback} onOpened          Triggers when the user opens the drop-down box
 * 
 *  @param {callback} onClosed          Triggers when the user closes the drop-down box
 * 
 *  @oaram {boolean} isOpened           true if the the drop-down is opened, false otherwise. Overrides the isOpened state
 * 
 *  @param {string} inputBoxValue       Current value of the input box when it works in fully uncontrolled mode.
 *                                      Useless when it works in fully controlled mode.
 * 
 *  @param {string} inputBoxRawValue    The same as value but before input preprocessing (removing leading and trailing
 *                                      whitespaces etc.)
 * 
 *    @param (string) cssSuffix           CSS class to append
 *  --------------------------------------------------------------------------------------------------------------------
 * 
 *  State:
 *  --------------------------------------------------------------------------------------------------------------------
 *  @oaram {boolean} isOpened           true if the the drop-down is opened, false otherwise.
 * 
 *  @param {string} inputBoxValue       Current value of the input box when it works in fully uncontrolled mode.
 *                                      Useless when it works in fully controlled mode.
 * 
 *  @param {string} inputBoxRawValue    The same as value but before input preprocessing (removing leading and trailing
 *                                      whitespaces etc.)
 *  --------------------------------------------------------------------------------------------------------------------
 */
export default class LoadableDropDownInput extends DropDownInput{

    /** Handles the input change of the box. (The state must be changed.)
     *  To be re-defined in subclasses
     * 
     *  @param {SyntheticEvent} the event that has been triggered
     */
    handleInputChange(event){
        super.handleInputChange(event);
        if (this.props.onInputChange){
            this.props.onInputChange(event);
        }
    }

    /** Renders children inside the drop down
     */
    renderChildren(){
        return (
            <div className={styles.drop_down_content}>
                {this.props.children}
            </div>
        );
    }

}