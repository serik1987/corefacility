import FieldManager, {ManagedField} from './field-manager.mjs';


/** Manages field where some duration (amount of days, hours, minutes, seconds, milliseconds) was represented.
 * 
 *  The model is immutable that means that you can't change the contained value in the model. You can just
 *  reveal new model with the same value.
 */
export class DurationManager extends FieldManager{

    DURATION_EXPRESSION = /^(?:(?<days>-?\d+)\s(?:days\s)?)?(?<sign>-?)((?:(?<hours>\d+):)(?=\d+:\d+))?(?:(?<minutes>\d+):)?(?<seconds>\d+)(?:[\.,](?<microseconds>\d{1,6})\d{0,6})?$/;
    MICROSECONDS_MAX_DIGITS = 6;

    /* Number of seconds in one day */
    DAY_DURATION = 86400.0;

    /* Number of seconds in one hour */
    HOUR_DURATION = 3600.0;

    /* Number of seconds in one minute */
    MINUTE_DURATION = 60.0;

    /* Number of microseconds in one second */
    MICROSECOND_DURATION = 1e-6;

    /** Constructs the duration manager
     * 
     *  @param {Entity|null} entity the parent entity of the duration
     *  @param {string|null} propertyName The entity property that is represented by this widget
     *  @param {any} defaultValue the value that will be represented by the manager when 
     *                            value is empty
     *  @param {object} options useless
     */
    constructor(entity, propertyName, defaultValue, options){
        super(entity, propertyName, defaultValue, options);
        this.internalValue = defaultValue;
    }

    /** Internal value */
    set internalValue(value){
        super.internalValue = value;
        
        if (value === null || value === undefined){
            this._seconds = NaN;
            return;
        }

        let matches = `${value}`.match(this.DURATION_EXPRESSION);
        if (matches === null){
            this._seconds = NaN;
            return;
        }

        let sign;
        if (sign === "-"){
            sign = -1;
        } else {
            sign = 1;
        }

        let microseconds;
        if (matches.groups.microseconds === undefined){
            microseconds = 0.0;
        } else {
            microseconds = parseInt(matches.groups.microseconds.padEnd(this.MICROSECONDS_MAX_DIGITS, "0"));
        }

        this._seconds = 0.0;
        this.__addDuration(matches.groups.days, this.DAY_DURATION);
        this.__addDuration(matches.groups.hours, this.HOUR_DURATION);
        this.__addDuration(matches.groups.minutes, this.MINUTE_DURATION);
        this.__addDuration(matches.groups.seconds, 1.0);
        this.__addDuration(microseconds, this.MICROSECOND_DURATION);
        this._seconds *= sign;
    }

    /** Adds to total duration to a given value
     * 
     *  @param {undefined|null|string|Number} what value is required to be added to the duration
     *  @param {Number} factor this value will be multiplied by this factor before add
     */
    __addDuration(value, factor = 1.0){
        if (value === null || value === undefined){
            value = 0.0;
        }
        this._seconds += value * factor;
    }

    /** 1 if duration is positive, -1 if duration is negative, 0 if duration is zero */
    get sign(){
        if (this._seconds > 0){
            return 1;
        } else if (this._seconds === 0){
            return 0;
        } else {
            return -1;
        }
    }

    /** Number of days */
    get days(){
        return Math.floor(Math.abs(this._seconds) / this.DAY_DURATION);
    }

    /** Number of hours */
    get hours(){
        return Math.floor(Math.abs(this._seconds) % this.DAY_DURATION / this.HOUR_DURATION);
    }

    /** Number of minutes */
    get minutes(){
        return Math.floor(Math.abs(this._seconds) % this.HOUR_DURATION / this.MINUTE_DURATION);
    }

    /** Number of seconds */
    get seconds(){
        return Math.floor(Math.abs(this._seconds) % this.MINUTE_DURATION);
    }

    /** Number of microseconds */
    get microseconds(){
        return Math.round((this._seconds - Math.floor(this._seconds)) / this.MICROSECOND_DURATION);
    }

    toString(){
        return this._seconds + " seconds";
    }

}


/** The field is responsible for representation of the stimulus duration.
 */
export default class DurationField extends ManagedField{

    /** Creates new DurationField
     */
    constructor(){
        super(DurationManager);
    }

    /** Accepts value from the React.js component and returns the value that will be sent to the
     *      external source.
     *  Also this method provides validation and must throw ValidationError if the value provided
     *      by the React.js components are not valid
     *  @param {Entity} entity      The Entity this value belongs to
     *  @param {string} name        Name of the entity field
     *  @param {any} value          Value received from React.js components
     *  @return {any}               Value that will be sent to external source
     */
    proofread(entity, propertyName, value){
        if (!(value instanceof DurationManager)){
            throw new TypeError("Only DurationManager can be assigned to this field!");
        }
        
        let hours = `${value.hours}`.padStart(2, "0");
        let minutes = `${value.minutes}`.padStart(2, "0");
        let seconds = `${value.seconds}`.padStart(2, "0");
        let string = `${hours}:${minutes}:${seconds}`;

        if (value.days !== 0){
            string = `${value.days} ${string}`;
        }
        if (value.sign === -1){
            string = "-" + string;
        }
        if (value.microseconds !== 0){
            string += `.${value.microseconds}`.padStart(6, "0");
        }

        return string;
    }

}