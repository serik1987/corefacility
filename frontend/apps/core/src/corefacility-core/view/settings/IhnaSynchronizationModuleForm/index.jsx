import {translate as t} from 'corefacility-base/utils';
import Label from 'corefacility-base/shared-view/components/Label';
import CheckboxInput from 'corefacility-base/shared-view/components/CheckboxInput';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import RadioInput from 'corefacility-base/shared-view/components/RadioInput'
import RadioButton from 'corefacility-base/shared-view/components/RadioButton';

import IhnaSynchronizationModule from 'corefacility-core/model/entity/IhnaSynchronizationModule';

import SynchronizationModuleForm from '../SynchronizationModuleForm';
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
 */
export default class IhnaSynchronizationModuleForm extends SynchronizationModuleForm{

    /** The entity class. The formObject will be exactly an instance of this class.
     *  The formObject is implied to be an instance of Entity
     */
    get entityClass(){
        return IhnaSynchronizationModule;
    }

    get fieldList(){
        return ["auto_add", "auto_update", "auto_remove", "ihna_website", "language", "page_length"];
    }

    /** Calculates the percent of synchronization completed.
     *  @return {object} result             The response body
     *  @return {number} percent            Completed percent number
     */
    calculatePercentage(result){
    	let completedStages = this.state.completedStages + 1;

    	console.log(result);
    	console.log(completedStages);


    	if (result.next_options === null){
    		return 100;
    	}

        switch (result.next_options.action){
        case "inverse":
        	return completedStages / (completedStages + 2) * 100;
        case "remove":
        	return completedStages / (completedStages + 1) * 100;
        default:
        	return super.calculatePercentage(result);
        }
    }

    /** Renders all settings for the module widget except Application status -> Enabled checkbox,
     *  Save Settings button and 'Settings was not saved' message
     */
    renderAuxiliarySettings(){
        return (
            [
                <Label>{t("Synchronization actions")}</Label>,
                <div className={styles.action_aligner}></div>,
                <div className={styles.action_container}>
                    <CheckboxInput
                        {...this.getFieldProps("auto_add")}
                        label={t("Add missed user accounts")}
                        tooltip={t("Creates accounts for all users that exist in the IHNA Website but " +
                            "doesn't exist in Corefacility")}
                    />
                    <CheckboxInput
                        {...this.getFieldProps("auto_update")}
                        label={t("Update user accounts")}
                        tooltip={t("Modifies all accounts in such a way as information entered there is " +
                            "line with the information published on the IHNA Website")}
                    />
                    <CheckboxInput
                        {...this.getFieldProps("auto_remove")}
                        label={t("Remove redundant users")}
                        tooltip={t("Removes all accounts that exist in Corefacility but doesn't exist in the " +
                            "IHNA website")}
                    />
                </div>,

                <Label>{t("The website address")}</Label>,
                <TextInput
                    {...this.getFieldProps("ihna_website")}
                    tooltip={t("Enter the address containing protocol name, domain name and the port only")}
                    htmlType="url"
                    />,
                
                <Label>{t("Website language")}</Label>,
                <RadioInput {...this.getFieldProps("language")} className={styles.language_container}>
                    <RadioButton value="ru" inactive={this.state.inactive}>{t("Russian")}</RadioButton>
                    <RadioButton value="en" inactive={this.state.inactive}>{t("English")}</RadioButton>
                </RadioInput>,

                <Label>{t("Loading page length")}</Label>,
                <TextInput
                    {...this.getFieldProps("page_length")}
                    tooltip={
                    	t("Number of user accounts that shall be downloaded from the IHNA website per one request")}
                />,
            ]
        );
    }

    /* prevState doesn't work here! Sorry :-( */
    componentDidUpdate(prevProps, prevState){
        let actionsState = this.state.rawValues.auto_add || this.state.rawValues.auto_update
        	|| this.state.rawValues.auto_remove;
        if (actionsState && !this.state.canBeActivated){
        	this.setState({
        		canBeActivated: true,
        		whyCantBeActivated: null,
        	});
        }
        if (!actionsState && this.state.canBeActivated){
        	this.setState({
        		canBeActivated: false,
        		whyCantBeActivated:
                        t("To activate the module please, turn on at least one Synchronization action"),
        	});
        	if (this.state.rawValues.is_enabled){
        		this.setState({
        			rawValues: {
        				...this.state.rawValues,
        				is_enabled: false,
        			}
        		});
        		this._formValues.is_enabled = false;
        		this._formObject.is_enabled = false;
        	}
        }

        super.componentDidUpdate(prevProps, prevState);
    }

}