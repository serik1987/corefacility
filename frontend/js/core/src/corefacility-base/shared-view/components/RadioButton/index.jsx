import * as React from 'react';
import styles from './style.module.css';


/** Defines the radio button. The radiobutton is also bi-state widget. But besides the BooleanInput, the user can set
 *  the radio button only to the true state. The widget state can be turned to false if the widget is a child of
 *  the RadioInput widget; when the user clicks on another widget that is an instance of RadioButton and which parent
 *  is RadioInput. Please, bear in mind that parent of the parent of this widget is not the parent of this widget.
 * 
 *  Props:
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {string} value           The value of the widget. If the radiobutton is in true state, value of the parent
 *                                  RadioInput widget is the same as the value of a given widget.
 * 
 *  @param {string} error           Error message to show below the widget
 * 
 *  @param {tooltip} tooltip        A small text that will be displayed when the mouse is hovered.
 * 
 *  @param {boolean} inactive       When the widget is inactive, the user can't click on it,
 * 
 *  @param {boolean} disabled       When the widget is disabled this is marked as disabled.
 * 
 *  @param {Component} children     Label to show
 *  --------------------------------------------------------------------------------------------------------------------
 * 
 *  State:
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {boolean} value          true is the user has been recently pressed on this radio button. false if the user
 *                                  has been recently pressed on another radio button
 *  --------------------------------------------------------------------------------------------------------------------
 */
export default class RadioButton extends React.Component{

    constructor(props){
        super(props);
        this.handleClick = this.handleClick.bind(this);

        this.state = {
            value: false,
        }
    }

    /** The state of the widget
     */
    get value(){
        if (this.props._value !== undefined){
            return this.props._value;
        } else {
            return this.state.value;
        }
    }

    /** Handles the user click: switches the widget state to true and attaches value field to the event target.
     *  If the widget doesn't change it's state the click event will not be propagated to the parent.
     * 
     *  @param {SyntheticEvent} event       The event that has been triggered this callback
     *  @return {undefined}                 Nothing.
     */
    handleClick(event){
        if (this.props.inactive || this.props.disabled){
            return;
        }
        if (!this.value){
            this.setState({value: true});
            event.target.value = this.props.value;
        } else {
            event.stopPropagation();
        }
    }

    shouldComponentUpdate(nextProps, nextState){
        return this.state.value !== nextState.value || this.props.error !== nextProps.error ||
            this.props.tooltip !== nextProps.tooltip || this.props.inactive !== nextProps.inactive ||
            this.props.disabled !== nextProps.disabled || this.props._value !== nextProps._value;
    }

    render(){
        let wrapperClasses = styles.wrapper;
        if (this.props.disabled){
            wrapperClasses += ` ${styles.disabled}`;
        }
        if (this.props.inactive){
            wrapperClasses += ` ${styles.inactive}`;
        }

        return (
            <div className={`${styles.box} radio-button`}>
                <div className={wrapperClasses} onClick={this.handleClick} title={this.props.tooltip}>
                    <div className={styles.button_wrapper}>
                        {this.value && <div className={styles.button}></div>}
                    </div>
                    <label>{this.props.children}</label>
                </div>
                {this.props.error && <p className={styles.error_message}>{this.props.error}</p>}
            </div>
        );
    }

}