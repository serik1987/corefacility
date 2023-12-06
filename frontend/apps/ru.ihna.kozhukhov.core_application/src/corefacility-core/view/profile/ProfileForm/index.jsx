import {translate as t} from 'corefacility-base/utils';

import Profile from 'corefacility-base/model/entity/Profile';
import UpdateForm from 'corefacility-base/view/UpdateForm';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import AvatarUploader from 'corefacility-base/shared-view/components/AvatarUploader';
import CredentialsOutput from 'corefacility-base/shared-view/components/CredentialsOutput';
import ModuleWidgets from 'corefacility-base/shared-view/components/ModuleWidgets';
import Scrollable from 'corefacility-base/shared-view/components/Scrollable';

import CoreWindowHeader from 'corefacility-core/view/base/CoreWindowHeader';

import PasswordChanger from '../PasswordChanger';
import style from './style.module.css';


/** This form shows profile user and allows to update it.
 * 
 * 	Such data have the following flow:
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
 * 
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
 * 									will be substituted. Such an object must contain
 * 									the 'lookup' button
 * 
 * 		@param {function} on404		The function will be evoked when the server received
 * 									error 404 during the reload or update. We recommend
 * 									you to use this.handle404 when the parent widget is
 * 									an instance of CoreWindow
 * 
 *      @param {function} onAuthorizationMethodSetup triggers when the user chooses a given authorization method
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
 *      @param {boolean} authorizationWidgetsAreVisible     true - show authorization widgets, false - hide them
 */
export default class ProfileForm extends UpdateForm{

    constructor(props){
        super(props);
        this.onAuthorizationWidgetsEmpty = this.onAuthorizationWidgetsEmpty.bind(this);
        this.setupAuthorizationMethod = this.setupAuthorizationMethod.bind(this);

        this.state = {
            ...this.state,
            authorizationWidgetsAreVisible: true,
        }
    }

    /** The entity class. The formObject will be exactly an instance of this class.
     *  The formObject is implied to be an instance of Entity
     */
    get entityClass(){
        return Profile;
    }

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return ['login', 'name', 'surname', 'email', 'phone', 'unix_group', 'home_dir', 'password'];
	}

    /** Return default values. The function is required if you want the resetForm to work correctly
     *  Each field must be mentioned!
     *  @async
     *      @param {object} inputData some input data passed to the form (They could be undefined)
     *      @return {object} the defaultValues
     */
    async getDefaultValues(inputData){
        let defaultValues = {};
        this.setState({
            "reloadError": this.__reloadError = null,
        });
        try{
            this._defaultObject = await window.application.user.reload();
            for (let field of this.fieldList){
                defaultValues[field] = this._defaultObject[field];
            }
            this.setState({
                "reloadError": this.__reloadError = null,
            });
        } catch (error){
            for (let field of this.fieldList){
                defaultValues[field] = null;
            }
            this.setState({
                "reloadError": this.__reloadError = error,
            });
        }
        return defaultValues;
    }

    /**
     * Window and form header
     */
    get header(){
        let header = `${this.state.rawValues.name} ${this.state.rawValues.surname}`.trim();
        if (header.length === 0){
            header = t("Profile");
        }
        return header;
    }

	/** Renders the form given that the updating entity was successfully loaded.
	 * 		@return {React.Component} Rendered content.
	 */
	renderContent(){
		return (
			<CoreWindowHeader
				{...this.getMessageBarProps()}
				header={this.header}
			>
                <Scrollable>
                    <form className={`window-form ${style.main}`}>
                        <div className={style.information_row}>
                            <section className={style.personal}>
                                <h2>{t("Personal Data")}</h2>
                                <div className={style.subsection_main}>
                                    <Label>{t("Login")}</Label>
                                    <Label>{this._formObject && this._formObject.login}</Label>

                                    <Label>{t("First name")}</Label>
                    				<TextInput
                                        {...this.getFieldProps('name')}
                                        tooltip={t("The first name is required for better visualization")}
                                        maxLength={100}
                                    />

                                    <Label>{t("Last name")}</Label>
                                    <TextInput
                                        {...this.getFieldProps('surname')}
                                        tooltip={t("The Last name is required for better visualization")}
                                        maxLength={100}
                                    />
                                </div>
                                <div className={style.subsection_contact}>
                                    <Label>{t("E-mail")}</Label>
                                    <TextInput
                                        {...this.getFieldProps('email')}
                                        htmlType="email"
                                        tooltip={t("The e-mail will be used for password recovery service and sending another notifications")}
                                        maxLength={254}
                                    />

                                    <Label>{t("Phone number")}</Label>
                                    <TextInput
                                        {...this.getFieldProps('phone')}
                                        htmlType="phone"
                                        tooltip={t("When suspicious activity was detected, please, call the user using this phone number: the user can confirm or deny this operation")}
                                        maxLength={20}
                                    />
                                </div>
                            </section>
                            <section className={style.avatar_wrapper}>
                                <h2>{t("Avatar")}</h2>
                                <AvatarUploader
                                    {...this.getChildComponentProps("avatar")}
                                    fileManager={this._formObject && this._formObject.avatar}
                                    tooltip={t("The user photo facilitates distinguising users among each other. This is not necessary to use your real photo.")}
                                    width={150}
                                    height={150}
                                />
                            </section>
                        </div>
                        <section>
                            <h2>{t("SSH Access Details")}</h2>
                            <div className={style.credentials}>
                                <Label>{t("UNIX account name")}</Label>
                                <CredentialsOutput>{this._formObject && this._formObject.unix_group}</CredentialsOutput>
                                {window.SETTINGS.user_can_change_password && [
                                    <Label>{t("Password")}</Label>,
                                    <PasswordChanger {...this.getFieldProps('password')}/>
                                ]}
                                <Label>{t("Home directory")}</Label>
                                <CredentialsOutput>{this._formObject && this._formObject.home_dir}</CredentialsOutput>
                            </div>
                        </section>
                        {this.state.authorizationWidgetsAreVisible && <section>
                            <h2>{t("Authorization methods")}</h2>
                            <ModuleWidgets
                                parentModuleUuid={window.application.model.uuid}
                                entryPointAlias="authorizations"
                                onClick={this.setupAuthorizationMethod}
                                inactive={this.state.inactive}
                                onWidgetsEmpty={this.onAuthorizationWidgetsEmpty}
                            />
                        </section>}
                        {this.renderEntityState()}
                        <div className={style.controls_row}>
                            <PrimaryButton {...this.getSubmitProps()}>{t("Save")}</PrimaryButton>
                            <PrimaryButton {...this.getSubmitProps()} onClick={this.handleSubmitAndClose}>{t("Save and close")}</PrimaryButton>
                        </div>
                    </form>
                </Scrollable>
			</CoreWindowHeader>
		);
	}

    /** Redirection route for "Save and close" and "Close" buttons
     */
    get entityListRoute(){
        return '/';
    }

    componentDidUpdate(prevProps, prevState){
        if (!this.props.onNameChange){
            return;
        }

        if (prevState.rawValues.name !== this.state.rawValues.name || prevState.rawValues.surname !== this.state.rawValues.surname){
            this.props.onNameChange(this.header);
        }
    }

    /**
     * Triggers when there are no uploaded external authorization methods
     */
    onAuthorizationWidgetsEmpty(){
        this.setState({authorizationWidgetsAreVisible: false});
    }

    /**
     * Triggers when the user clicks on the external authorization method
     * @async
     * @param {ModuleWidget} authorizationWidget the authorization module selected by the user
     */
    async setupAuthorizationMethod(authorizationWidget){
        if (this.props.onAuthorizationMethodSetup){
            await this.props.onAuthorizationMethodSetup(authorizationWidget);
        }
    }

}