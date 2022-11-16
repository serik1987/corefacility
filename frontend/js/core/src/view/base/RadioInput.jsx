import * as React from 'react';

import RadioButton from './RadioButton.jsx';



/** Represents a group of radio buttons and manages switching between them.
 * 
 * 	The widget could be used as container for several radiobuttons. Each child radiobutton inside the container (the
 *  of its child is not its child!) can have one of two states: false, true. The container automatically changes
 *  states of the child radiobuttons in such a way as no two or more radiobuttons could have the true state. The user
 *  can change the state of all radiobuttons by clicking on one of them. The radiobutton which the user has clicked
 *  will turn to true state, all other child radiobuttons will turn to the false state.
 *
 *  Each radiobutton has 'value' prop which value is some arbitrary string. Value of the value props doesn't affect on
 *  the work of the radiobutton child and is not related to the child's state (true or false). However, the value of
 *  the RadioInput is claimed to be the value of the 'value' prop of the child radiobutton which state is true. If no
 *  such radiobuttons exist, the value of this widget is claimed to be null.
 *
 *  The widget can work in one of two modes: fully controlled and fully uncontrolled. In the fully controlled mode
 *  the value of the widget is determined by its parent through the 'value' prop. If the user attempts to change the
 *  widget, such change will not have an effect until the parent widget modifies the 'value' prop.
 *
 *  In the fully uncontrolled mode the user is free to change the widget's value. However, the value can't be set by
 *  the parent.
 *
 *  Props:
 * ---------------------------------------------------------------------------------------------------------------------
 *  @param {callback} onInputChange         Triggers when the user changes the state of any child radiobuttons and hence
 *                                          modifies the state of the widget.
 *
 *  @param {string|null} value              Value of the widget in fully controlled mode. If you set the value to be
 *                                          undefined, the RadioInput mode is claimed to be fully uncontrollled.
 *
 *  @param {string|null} defaultValue       Value of the widget at the time of its create.
 *
 *  @param {string} className              The widget has no its own classes. Any classes that define CSS styles for
 *                                         the widget's HTML elements must be given here.
 * ---------------------------------------------------------------------------------------------------------------------
 *
 *  State:
 * ---------------------------------------------------------------------------------------------------------------------
 *  @param {string} value                   Current value of the widget
 * ---------------------------------------------------------------------------------------------------------------------
 */
export default class RadioInput extends React.Component{

    constructor(props){
        super(props);
        this.handleClick = this.handleClick.bind(this);

        this.state = {
            value: null,
        }

        if (this.props.defaultValue){
            this.state.value = this.props.defaultValue;
        }
    }

    /** Returns the widget value: the value prop for fully controlled mode or the value state for fully uncontrolled
     *  mode.
     */
    get value(){
        if (this.props.value !== undefined){
            return this.props.value;
        } else {
            return this.state.value;
        }
    }

    handleClick(event){
        if (typeof event.target.value !== "string" && typeof event.target.value !== "symbol"){
            return;
        }
        let value = event.target.value;
        event.target.value = undefined;
        this.setState({value: value});
        if (this.props.onInputChange){
            this.props.onInputChange({...event, value: value});
        }
    }

    render(){
        return (
            <div className={this.props.className} onClick={this.handleClick}>
                {this.props.children.map(component => {
                    if (component.type === RadioButton){
                        return React.cloneElement(component, {
                            _value: component.props.value === this.value,
                        });
                    }
                })}
            </div>
        );
    }

}