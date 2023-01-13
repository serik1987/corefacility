import {translate as t} from 'corefacility-base/utils';
import client from 'corefacility-base/model/HttpClient';
import User from 'corefacility-core/model/entity/User';

import Form from 'corefacility-base/view/Form';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import ModuleWidgets from 'corefacility-base/shared-view/components/ModuleWidgets';

import style from './style.module.css';
import {ReactComponent as Logo} from 'corefacility-base/shared-view/icons/logo.svg';


/** This is the base abstract class for all web forms.
 * 	The Web forms allow the user to interact with data and change them.
 *  The form manipulate with key => value pairs where key is some short
 *  string to identify certain value and value may have any type.
 * 	Each value is entered by the user in a stand-alone component.
 * 	We will refer to keys as 'field names'.
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
 * 									will be substituted.
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
 */
export default class AuthorizationForm extends Form{

	constructor(props){
		super(props);
		this.handleAuthorizationMethodClick = this.handleAuthorizationMethodClick.bind(this);
		this.handleAuxiliaryAuthorizationMethodsHide = 
			this.handleAuxiliaryAuthorizationMethodsHide.bind(this);

		this.state = {
			...this.state,
			extraAuthorizationMethods: true,
		}
	}

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return null;
	}

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@async
	 * 		@param {object} inputData some input data passed to the form (They could be undefined)
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		return {
			"login": null,
			"password": null,
		}
	}

	/** true if the form can be submitted (i.e., there are no field errors and global error, all required fields
	 * 	are not empty)
	 */
	get isSubmittable(){
		return this._formValues !== null && this._formValues.login !== null && this._formValues.password !== null;
	}

	/** Tells the form what to do if the user presses the 'Submit' buton. It could be
	 * 		posting new entity on the server, requesting for data processing - whenever
	 * 		you want!
	 * 
	 * 	HIGHLY IMPORTANT! Throw an error when the server-side validation fails only!
	 * 	If client-side validation fails, the function must just change and throw
	 * 	ValidationError with no arguments.
	 * 
	 *  @async
	 * 	@return {undefined} all the result is changes in this._formObject
	 * 		The function should throw an exception when server-side validation fails or
	 * 		modify the errors state when the client-side validation fails.
	 */
	async modifyFormObject(){
		let url = `/api/${window.SETTINGS.client_version}/login/`;
		let result = await client.post(url, this._formValues);
		let user = User._entityProviders[User.SEARCH_PROVIDER_INDEX].getObjectFromResult(result.user);

		this.setState({
			rawValues: {
				...this.state.rawValues,
				password: null,
			}
		});
		this._formValues.password = null;
		window.application.user = user;
		window.application.token = result.token;
	}

	handleAuthorizationMethodClick(widget){
		let url = new URL(window.location.href);
		url.pathname = `/authorize/${widget.alias}/`;
		url.searchParams.set('route', window.location.pathname);
		window.location = url;
	}

	handleAuxiliaryAuthorizationMethodsHide(event){
		this.setState({extraAuthorizationMethods: false});
	}

	render(){
		let loginForm = null;

		if (window.application.activationCode === null){
			loginForm = [
				<h2>{t("Log in")}</h2>,
				<div className={style.main_wrapper}>
					<div class={style.system_message}>
						{this.renderSystemMessage()}
					</div>
					<Label>{t("Login")}</Label>
					<TextInput {...this.getFieldProps("login")}/>
					<Label>{t("Password")}</Label>
					<TextInput {...this.getFieldProps("password")} htmlType="password"/>
				</div>,
				<div className={style.button_wrapper}>
					<PrimaryButton {...this.getSubmitProps()}>{t("Authorize")}</PrimaryButton>
				</div>,
			];
			if (this.state.extraAuthorizationMethods){
				loginForm.splice(2, 0, <div className={style.widgets_wrapper}>
					<h2>{t("... or authorize through")}</h2>
					<ModuleWidgets
						parentModuleUuid={window.application.model.uuid}
						entryPointAlias="authorizations"
						onClick={this.handleAuthorizationMethodClick}
						onWidgetsEmpty={this.handleAuxiliaryAuthorizationMethodsHide}
					/>
				</div>);
			}
		}
		if (window.application.activationCode !== null && window.application.token === null){
			loginForm = [
				<h2>{t("Account activation")}</h2>,
				<p>{t("This activation link is wrong or has been expired. Please, try again.")}</p>,
				<div className={style.button_wrapper}>
					<a href="/">{t("Main Page")}</a>
				</div>
			];
		}
		if (window.application.activationCode !== null && window.application.token !== null){
			loginForm = [
				<h2>{t("Account activation")}</h2>,
				<p>{t("Your account has been successfully activated. Please, use the following credentials to login:")}</p>,
				<dl>
					<dt>{t("Application URL")}</dt>
					<dd>{window.location.origin}</dd>
					<dt>{t("Login")}</dt>
					<dd>{window.SETTINGS.login}</dd>
					<dt>{t("Password")}</dt>
					<dd>{t(window.SETTINGS.password)}</dd>
				</dl>,
				<p>{t("Please, remember or write down these credentials since you will see them just once")}</p>,
				<div className={style.button_wrapper}>
					<a href="/">{t("Main Page")}</a>
				</div>
			];
		}

		return (
			<div className={style.form_wrapper}>
				<div className={style.form}>
					<div className={style.logo_wrapper}>
						<Logo/>
					</div>
					<h1>Corefacility</h1>
					{loginForm}
				</div>
			</div>
		);
	}

	componentDidMount(){
		this.resetForm();
		document.getElementsByTagName("title")[0].innerText = t("Log in");
		if (window.SETTINGS.authorization_error !== null && window.SETTINGS.authorization_error !== undefined){
			this.setState({
				globalError: window.SETTINGS.authorization_error
			});
			window.SETTINGS.authorization_error = null;
		}
	}

}