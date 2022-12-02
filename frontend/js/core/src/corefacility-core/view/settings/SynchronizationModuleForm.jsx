import {translate as t} from 'corefacility-base/utils';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';

import ModuleForm from './ModuleForm';

/** This is a base class for all forms that can be used to adjust single module settings.
 * 
 * 	There is following dataflow within the module settings form
 * 
 * 	inputData => defaultValues => rawValues => formValues => formObject => modifyFormObject
 * 
 * 	inputData - a short object that is necessary to build defaultValues.
 * 
 * 	defaultValues - values before the user interactions. These data may
 * 		be downloaded from the external server (in case when user modifies
 * 		the object) or can be simply preliminary set of values (in case
 * 		when user creates new object)
 * 
 * 	rawValues - values entered by the user These values are part of the component
 * 		state: all fields are rendered according to rawValues.
 * 
 * 	formValues - values after primitive proprocessing (i.e., removing loading
 * 		and trailing whitespaces, converting to proper Javascript type, converting
 * 		empty strings to null etc.). These values don't influence on rendering
 * 		of fields.
 * 
 * formObject - strictly must be an instance of Entity.
 * 		On the one hand, formObject is responsible for client-side data validation.
 * 		i.e., it accepts invalidated data from the formValues and must reveal the
 * 		validated data or throw an exception if client-side validation fails.
 * 		On the other side, formObject is the only intermediate that is responsible
 * 		for information exchange between the form and the rest of the world, including
 * 		other components.
 * 
 * 	modifyFormObject - when the formObject is constructedm the modifyFormObject
 * 		becomes the main form function
 * 
 * Props:
 * 		@param {object} options		Auxiliary options to be passed to the form.
 * 									They depend on certain subclass specification.
 * 
 * 		@param {object} inputData	When the prop equals to null or undefined,
 * 									the resetForm() method will not be invoked after
 * 									form mounting or pressing the Reload button from
 * 									the main menu. When the prop equals to object,
 * 									the resetForm() will be invoked during the mount
 * 									or press the reload() button and these input data
 * 									will be substituted.
 * 
 * 		@param {function} on404		The function will be evoked when the server received
 * 									error 404 during the reload or update. We recommend
 * 									you to use this.handle404 when the parent widget is
 * 									an instance of CoreWindow
 * 
 * 		@param {callback} onSettingsBeforeSave triggers before save of the settings
 * 		@param {callback} onSettingsAfterSave  triggers after save of the settings
 * 		@param {callback} onSettingsSaveError  triggers when error occured during the settings save
 * 
 * State:
 * 		@param {object} rawValues	values as they have been entered by the user
 * 
 * 		@param {object} errors 		Field errors. The field error is defined for
 * 			a certain field (e.g., Incorrect e-mail, phone is not filled etc.).
 * 			This state has a form key => value where where key is field name and
 * 			value is error message corresponding to it
 * 
 * 		@param {string} globalError The error unrelated to any of the fields
 * 			(e.g., authentication failed, network disconnected etc.)
 * 
 * 		@param {boolean} inactive	When the form interacts with the server
 * 			(e.g., fetches or posts the data) its interaction with the rest of
 * 			the world is also impossible
 *
 * 		@param {string} redirect	if string, the form will be redirect to the React.js
 * 									route pointed out in this property. If null, no redirection
 * 									will be provided.
 * 
 *      @param {boolean} canBeActivated true if the module can be activated, false otherwise
 * 
 *      @param {string} whyCantBeActivated why the module can't be activated?
 * 
 *      @param {string} additionalNotification An additional error message that shall be placed on the module
 *                                             when the module can be activated and the field value is valid.
 * 
 *      @param {Symbol|float} synchronizationProgress one of the following values:
 *              this.SYNCHRONIZATION_PROGRESS_SETTINGS the user is changing the synchronization settings
 *              this.SYNCHRONIZATION_PROGRESS_STARTING the user clicked on the 'Save and Synchronize' button,
 *                      but the synchronization process is going to be started
 *              some float number - the synchronization is in progress, the progress bar reflects how many stages
 *                      have been completed.
 *              this.SYNCHRONIZATION_PROGRESS_FINISHED the synchronization process has been already done.
 *              this.SYNCHRONIZATION_PROGRESS_CANCELLED the user cancelled the synchronization process
 */
 export default class SynchronizationModuleForm extends ModuleForm{

    constructor(props){
        super(props);
        this.handleSynchronize = this.handleSynchronize.bind(this);

        this.state = {
            ...this.state,
            synchronizationProgress: SynchronizationProgress.settings,
        }
    }

    /** Triggers when the user click on the 'Save and Synchronize' button */
    async handleSynchronize(event){
        if (!this._formObject.is_enabled){
            this.setState({
                additionalNotification: t("The synchronization can't be started until this module is disabled"),
            });
            return;
        }
        await this.handleSubmit(event);
        this.setState({
            synchronizationProgress: SynchronizationProgress.starting,
        });
    }

    /** Triggers when the user changes the value in the field.
     * 
     * 
     *  @param {string} name the field name where user changes the value
     *  @param {SyntheticEvent} the event triggered by the object. Because the value
     *      preprocessing is made by the field individually, the event must have the
     *      following fields:
     *          event.target.value - the value before preprocessing (raw value)
     *          event.value - the value after preprocessing
     *  @return {undefined}
     */
    handleInputChange(name, event){
        this.setState({additionalNotification: null});
        super.handleInputChange(name, event);
    }

    /** Evokes when the user presses the Submit button.
     * 
     *  @param {SyntheticEvent} the event triggered by the submission button
     *  @return {boolean} true if the form was successfully submitted, false otherwise
     */
    async handleSubmit(event){
        this.setState({additionalNotification: null});
        await super.handleSubmit(event);
    }

    renderAuxiliaryControls(){
        return <PrimaryButton onClick={this.handleSynchronize}>{t("Save and Synchronize")}</PrimaryButton>;
    }

    render(){
        if (this.state.synchronizationProgress === SynchronizationProgress.settings){
            return super.render();
        } else {
            return (
                <p>Rendering the synchronization form...</p>
            )
        }
    }
 	
 }

 let SynchronizationProgress = {
    settings: Symbol("settings"),
    starting: Symbol("starting"),
    finished: Symbol("finished"),
    cancelled: Symbol("cancelled"),
 }
 Object.freeze(SynchronizationProgress);