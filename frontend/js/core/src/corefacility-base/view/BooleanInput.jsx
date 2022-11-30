import * as React from 'react';

import {NotImplementedError} from 'corefacility-base/exceptions/model';


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
 *      @param {boolean} inactive           When equals to true, the user can't change the widget's value by
 *                                          just clicking on it
 * 
 *      @param {boolean} disabled           When equals to true, they widget is marked as grey and the user
 *                                          can't change its value by just clicking on it
 * 
 * 	State:
 * 		@param {boolean} value 				Useless in parent-controlled mode. However, in pareent-uncontrolled
 * 											mode it reflects a component state currently set by the user.
 */
export default class BooleanInput extends React.Component{

    constructor(props){
        super(props);
        this.handleClick = this.handleClick.bind(this);
        this.state = {
            value: false,
        }
        if (this.props.defaultValue){
            this.state.value = true;
        }
    }

    /* State of the widget */
    get value(){
        if (this.props.value === undefined){
            return this.state.value;
        } else if (this.props.value === null){
            return false;
        } else {
            return this.props.value;
        }
    }

    /** This function must be evoked when the user tries to the the state of the input
     *  So, if you create subclass of the BooleanInput, don't forget to pass this function
     *  as event handler.
     * 
     *      @param {SyntheticEvent} event   The event object of the mouse clicking event
     *      @return {undefined}
     */
    handleClick(event){
        if (this.props.inactive || this.props.disabled){
            return;
        }

        let value = !this.value;
        this.setState({value: value});
        if (this.props.onInputChange){
            event.target.value = value;
            this.props.onInputChange({...event, value: value});
        }
    }

	render(){
		throw new NotImplementedError("render");
		return null;
	}

}