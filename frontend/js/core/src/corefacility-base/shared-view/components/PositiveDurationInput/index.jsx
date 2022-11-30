import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';
import {DurationManager} from 'corefacility-base/model/fields/DurationField';

import TextInput from '../TextInput';
import styles from './style.module.css';


/** Represents widget for I/O of the duration values. All negative durations will be transformed into positive ones.
 * 
 *  The widget can work in parent-controlled and user-controlled modes. In parent-controlled mode the widget value
 *  is fully controlled by the parent widget. The user can change the widget's value only when the parent provides
 *  feedback (e.g., Form, UpdateForm, CreateForm provide this).
 * 
 *  In user-controlled mode the widget value is fully controlled by the use. The user can change the widget value
 *  without any preconditions. However, the parent can't set the widget value.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 *  @param {callback} onInputChange         Triggers when the user enters a valid duration value. You must set this
 *                                          property in the parent-controlled mode, otherwise the user will not be
 *                                          able to change the widget value.
 *  @param {DurationManager|null} value     First, this prop defines the mode. If its value is undefined the mode is
 *                                          stated to be user-controlled. If this value equals to null or
 *                                          DurationManager instance, the mode is stated to be parent-controlled.
 *                                          In the parent-controlled mode, this is a DurationManager value that is
 *                                          passed from the parent component to a given component.
 *  @param {DurationManager} defalutValue   In user-controlled mode, defines the value of the component at the
 *                                          constructor execution time.
 *                                          In parent-controlled mode, this prop is useless.
 *  @@param {string} error                  In parent-controlled mode, value of the error that will be passed from
 *                                          the parent to the given component prividing that all fields were correctly
 *                                          filled by the user.
 *  @param {string} tooltip                 The text to be displayed when the user hovers a widget
 *  @param {boolean} disabled               When the widget is disabled, all its input fields are disabled.
 *  @param {boolean} inactive               When the widget is inactive, all its input fields are inactive.
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 *  @param {DurationManager} value          The duration value to be set.
 *  @param {number} days                    Number of days from the value (on blur) or user input (on focus)
 *  @param {number} hours                   Number of hours from the value (on blur) or user input (on focus)
 *  @param {number} minutes                 Number of minutes from the value (on blur) or user input (on focus)
 *  @param {number} seconds                 Number of seconds from the value (on blur) or user input (on focus)
 *  @param {number} microseconds            Number of microseconds from the value (on blur) or user input (on focus)
 *  @param {string} error                   Error occured during the user input
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class PositiveDurationInput extends React.Component{

    /** Provides information about how to process input from the TextInput-s.
     * 
     *  field names is corresponding field in the DurationManager
     *  field values are objects in the following field;
     *      factor - the input value will be multiplied by this factor in order to set the increment of the total
     *               duration in seconds
     *      minValue - the user can't print the value less than this input
     *      maxValue - the user can't print the value greater than this input
     */
    WIDGET_IDENTITIES = {
        days: {
            factor: 86400.0,
            minValue: -Infinity,
            maxValue: Infinity,
        },
        hours: {
            factor: 3600.0,
            minValue: 0,
            maxValue: 23,
        },
        minutes: {
            factor: 60.0,
            minValue: 0,
            maxValue: 59,
        },
        seconds: {
            factor: 1.0,
            minValue: 0,
            maxValue: 59,
        },
        microseconds: {
            factor: 1e-6,
            minValue: 0,
            maxValue: 999999,
        }
    }

    constructor(props){
        super(props);
        this.handleInputBlur = this.handleInputBlur.bind(this);

        let initialValue;
        if (this.props.defaultValue === undefined){
            initialValue = new DurationManager(null, null, 0, {});
        } else {
            initialValue = this.props.defaultValue;
        }
        if (initialValue === null){
            initialValue = new DurationManager(null, null, 0, {});
        }

        this.state = {
            value: initialValue,
            days: initialValue.days,
            hours: initialValue.hours,
            minutes: initialValue.minutes,
            seconds: initialValue.seconds,
            microseconds: initialValue.microseconds,
            error: null,
        }
    }

    /** Value to output */
    get value(){
        if (this.props.value === undefined){
            return this.state.value;
        } else {
            return this.props.value;
        }
    }

    /** Error to be displayed
     */
    get error(){
        if (this.state.error !== null){
            return this.state.error;
        } else {
            return this.props.error;
        }
    }

    /** Triggers when the user changes value in any text input.
     *  @param {SyntheticEvent} event           The event to be triggered.
     *  @param {string} identity                The identity of the widget that triggered this event. One of the
     *                                          following values are allowed:
     *                                          'days', 'hours', 'minutes', 'seconds', 'microseconds'
     */
    handleInputChange(event, identity){
        let {factor, minValue, maxValue} = this.WIDGET_IDENTITIES[identity];
        let value = event.value;
        this.setState({[identity]: event.target.value, error: null});

        if (value === null){
            this.setState({error: t("Empty values are not allowed")});
            return;
        }

        if (!value.match(/^\d+$/)){
            this.setState({error: t("The value must be a number")});
            return;
        }
        value = parseInt(value);

        if (value < minValue){
            this.setState({error: t("The value must not be less than ") + minValue});
            return;
        }

        if (value > maxValue){
            this.setState({error: t("The value must not be greater than ") + maxValue});
        }

        let time = 0.0;
        for (let localIdentity of ['days', 'hours', 'minutes', 'seconds', 'microseconds']){
            let localValue;
            if (localIdentity === identity){
                localValue = value;
            } else {
                localValue = this.state[localIdentity];
            }

            time += localValue *= this.WIDGET_IDENTITIES[localIdentity].factor;
        }
        let newDuration = new DurationManager(this.value.entity, this.value.propertyName, time, {});

        this.setState({value: newDuration});
        if (this.props.onInputChange){
            this.props.onInputChange({value: newDuration, target: {value: newDuration}});
        }
    }

    /** Triggers when the input loses the focus
     *  @param {SyntheticEvent|null} event   the event that triggered this function
     */
    handleInputBlur(event){
        this.setState({
            days: this.value.days,
            hours: this.value.hours,
            minutes: this.value.minutes,
            seconds: this.value.seconds,
            microseconds: this.value.microseconds,
            error: null,
        });
    }

	render(){
		return (
            <div>
                <div className={styles.duration_container} title={this.props.tooltip}>
                    <div className={styles.duration_item}>
                        <TextInput
                            onInputChange={event => this.handleInputChange(event, "days")}
                            onBlur={this.handleInputBlur}
                            value={this.state.days}
                            disabled={this.props.disabled}
                            inactive={this.props.inactive}
                            maxLength={2}/>
                        <span>{t("days")}</span>
                    </div>
                    <div className={styles.duration_item}>
                        <TextInput
                            onInputChange={event => this.handleInputChange(event, "hours")}
                            onBlur={this.handleInputBlur}
                            value={this.state.hours}
                            disabled={this.props.disabled}
                            inactive={this.props.inactive}
                            maxLength={2}/>
                        <span>{t("hours")}</span>
                    </div>
                    <div className={styles.duration_item}>
                        <TextInput
                            onInputChange={event => this.handleInputChange(event, "minutes")}
                            onBlur={this.handleInputBlur}
                            value={this.state.minutes}
                            disabled={this.props.disabled}
                            inactive={this.props.inactive}
                            maxLength={2}/>
                        <span>{t("minutes")}</span>
                    </div>
                    <div className={styles.duration_item}>
                        <TextInput
                            onInputChange={event => this.handleInputChange(event, "seconds")}
                            onBlur={this.handleInputBlur}
                            value={this.state.seconds}
                            disabled={this.props.disabled}
                            inactive={this.props.inactive}
                            maxLength={2}/>
                        <span>{t("seconds")}</span>
                    </div>
                    <div className={styles.duration_item}>
                        <TextInput
                            onInputChange={event => this.handleInputChange(event, "microseconds")}
                            onBlur={this.handleInputBlur}
                            value={this.state.microseconds}
                            disabled={this.props.disabled}
                            inactive={this.props.inactive}
                            maxLength={6}/>
                        <span>{t("microseconds")}</span>
                    </div>
                </div>
                {this.error !== null && <p className={styles.error_container}>{this.error}</p>}
            </div>
        );
	}

    componentDidMount(){
        if (this.props.value !== undefined){
            this.handleInputBlur(null);
        }
    }

    componentDidUpdate(prevProps, prevState){
        if (prevProps.value !== this.props.value && this.props.value !== undefined){
            this.handleInputBlur(null);
        }
    }

}