import {translate as t} from 'corefacility-base/utils';
import client from 'corefacility-base/model/HttpClient';
import Label from 'corefacility-base/shared-view/components/Label';
import ProgressBar from 'corefacility-base/shared-view/components/ProgressBar';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import {ReactComponent as AddIcon} from 'corefacility-base/shared-view/icons/add.svg';
import {ReactComponent as EditIcon} from 'corefacility-base/shared-view/icons/edit.svg';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/delete.svg';
import {ReactComponent as DefaultIcon} from 'corefacility-base/shared-view/icons/person.svg';

import ModuleForm from '../ModuleForm';
import styles from './style.module.css';

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
 *      @param {Symbol} synchronizationState Reflects the synchronization state:
 *          SynchronizationProgress.settings        The user is adjusting synchronization settings.
 *          SynchronizationProgress.starting        The synchronization has been started, the frontend is going to
 *                                                  send the very first synchronization request to the backend.
 *          SynchronizationProgress.pending         The synchronization has been started, the frontend waits for
 *                                                  response from the backend.
 *          SynchronizationProgress.error           The promise related to the last synchronization request has been
 *                                                  rejected.
 *          SynchronizationProgress.cancelling      The synchronization has been cancelled on the client side but
 *                                                  the backend doesn't know about it
 *          SynchronizationProgress.cancelled       The synchronization has been cancelled both on the frontend
 *                                                  and the backend sides.
 *          SynchronizationProgress.finished        The synchronization has been finished
 * 
 *  @param {number} percent         Number of percent completed.
 *  @oaram {string} error           The error happened during the last synchronization request
 */
 export default class SynchronizationModuleForm extends ModuleForm{

    SYNCHRONIZATION_URL = `/api/${window.SETTINGS.client_version}/account-synchronization/`;

    constructor(props){
        super(props);
        this.handleSynchronize = this.handleSynchronize.bind(this);
        this.handleSynchronizationClose = this.handleSynchronizationClose.bind(this);
        this.handlePause = this.handlePause.bind(this);
        this.handleResume = this.handleResume.bind(this);

        this.state = {
            ...this.state,
            synchronizationState: SynchronizationState.settings,
            percent: 0,
            error: null,
            options: null,
            completedStages: 0,
        }

        this._details = null;
    }

    /** Starts the synchronization process
     */
    async synchronize(){
        let options = this.state.options;

        try{
            while (options !== null){
                let result = await client.post(this.SYNCHRONIZATION_URL, options);
                let desiredState = SynchronizationState.pending;
                let isInterrupted = false;
                if (this.state.synchronizationState === SynchronizationState.cancelling && result.next_options !== null){
                    desiredState = SynchronizationState.cancelled;
                    isInterrupted = true;
                }
                this.setState({
                    synchronizationState: desiredState,
                    percent: this.calculatePercentage(result),
                    error: null,
                    options: result.next_options,
                    completedStages: this.state.completedStages + 1
                });
                this._details = [...this._details, ...result.details.map(errorInfo => {
                    return {
                        action: errorInfo.action,
                        user: `${errorInfo.surname} ${errorInfo.name}`,
                        message: errorInfo.message,
                    }
                })];
                options = result.next_options;
                if (isInterrupted){
                    return;
                }
            }

            this.setState({
                synchronizationState: SynchronizationState.finished,
                percent: 100,
                error: null,
                options: {},
            });

        } catch (error){
            this.setState({
                synchronizationState: SynchronizationState.error,
                error: error.message,
            });
        }
    }

    /** Calculates the percent of synchronization completed.
     *  @return {object} result             The response body
     *  @return {number} percent            Completed percent number
     */
    calculatePercentage(result){
        let completedStages = this.state.completedStages + 1;
        let percent = completedStages / (completedStages + 1) * 100;

        if (typeof result.total_steps === "number" && result.total_steps > 0){
            percent = completedStages / result.total_steps * 100;
        }

        return percent;
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
        if (window.SETTINGS.suggest_administration){
            await window.application.openModal("posix_action", {bashScript: ["python3 manage.py synchronize"]});
            return;
        }
        this.setState({
            synchronizationState: SynchronizationState.starting,
            percent: 0,
            error: null,
            options: {},
            completedStages: 0,
        });
    }

    /* Triggers when the user presses the "Close" button */
    handleSynchronizationClose(event){
        this.setState({
            synchronizationState: SynchronizationState.settings,
            percent: 0,
            error: null,
            options: null,
            completedStages: 0,
        });
    }

    /* Triggers press on the Pause button */
    handlePause(event){
        this.setState({
            synchronizationState: SynchronizationState.cancelling,
        });
    }

    /** Triggers press on Resume button */
    handleResume(event){
        this.setState({
            synchronizationState: SynchronizationState.pending,
            error: null,
        });
        this.synchronize();
    }

    /** Triggers when the user changes the value in the field.
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
        let synchronizationMessage, synchronizationMessageClasses, controls;

        let pauseButton = <PrimaryButton onClick={this.handlePause}>{t("Pause")}</PrimaryButton>;
        let closeButton = <PrimaryButton onClick={this.handleSynchronizationClose}>{t("Close")}</PrimaryButton>;
        let resumeButton = <PrimaryButton onClick={this.handleResume}>{t("Resume")}</PrimaryButton>;
        let tryAgainButton = <PrimaryButton onClick={this.handleResume}>{t("Try again.")}</PrimaryButton>;

        switch (this.state.synchronizationState){

        case SynchronizationState.settings:
            return super.render();

        case SynchronizationState.starting:
        case SynchronizationState.pending:
            synchronizationMessage = t("Synchronization") + "...";
            synchronizationMessageClasses = styles.synchronization_message;
            controls = [pauseButton];
            break;

        case SynchronizationState.finished:
            synchronizationMessage = t("Synchronization completed.");
            synchronizationMessageClasses = styles.synchronization_message;
            controls = [closeButton];
            break;

        case SynchronizationState.cancelling:
            synchronizationMessage = t("Stopping synchronization...");
            synchronizationMessageClasses = styles.synchronization_message;
            controls = [];
            break;

        case SynchronizationState.cancelled:
            synchronizationMessage = t("The synchronization was stopped.");
            synchronizationMessageClasses = styles.synchronization_message;
            controls = [resumeButton, closeButton];
            break;

        case SynchronizationState.error:
            synchronizationMessage = this.state.error;
            synchronizationMessageClasses = styles.synchronization_error;
            controls = [tryAgainButton];
            break;

        default:
            synchronizationMessage = "Серёга, сверстай это состояние. Ты что, забыл?";
            synchronizationMessageClasses = styles.synchronization_message;
            controls = [closeButton];
        }

        return (
            <div className={styles.synchronization_container}>
                <div className={synchronizationMessageClasses}>{synchronizationMessage}</div>
                <ProgressBar progress={this.state.percent}/>
                <div className={styles.synchronization_controls}>{controls}</div>
                {this._details !== null && this._details.length !== 0 && (
                    <div className={styles.error_container}>
                        {this._details.map(detailInfo => {
                            let {action, user, message} = detailInfo;
                            let icon = null;
                            switch (action){
                            case "add":
                                icon = <AddIcon/>;
                                break;
                            case "edit":
                                icon = <EditIcon/>;
                                break;
                            case "remove":
                                icon = <RemoveIcon/>;
                                break;
                            default:
                                icon = <DefaultIcon/>;
                            }
                            return [
                                icon,
                                <div>{user}</div>,
                                <div>{message}</div>
                            ];
                        })}
                    </div>
                )}
            </div>
        );
    }

    componentDidUpdate(prevProps, prevState){
        if (this.state.synchronizationState === SynchronizationState.starting){
            this.setState({
                synchronizationState: SynchronizationState.pending,
                percent: 0,
                error: null,
                options: {},
                completedStages: 0,
            });
            this._stageNumber = 0;
            this._details = [];
            this.synchronize();
        }
    }
 	
 }

 let SynchronizationState = {
    settings: Symbol("settings"),
    starting: Symbol("starting"),
    pending: Symbol("pending"),
    finished: Symbol("finished"),
    cancelling: Symbol("cancelling"),
    cancelled: Symbol("cancelled"),
    error: Symbol("error"),
 }
 Object.freeze(SynchronizationState);