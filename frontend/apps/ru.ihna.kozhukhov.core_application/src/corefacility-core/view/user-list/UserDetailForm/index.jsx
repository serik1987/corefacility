import {translate as t} from 'corefacility-base/utils';
import {tpl_password} from 'corefacility-base/template';
import {BadRequestError} from 'corefacility-base/exceptions/network';
import client from 'corefacility-base/model/HttpClient';
import User from 'corefacility-base/model/entity/User';
import UpdateForm from 'corefacility-base/view/UpdateForm';
import Scrollable from 'corefacility-base/shared-view/components/Scrollable';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import CheckboxInput from 'corefacility-base/shared-view/components/CheckboxInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import AvatarUploader from 'corefacility-base/shared-view/components/AvatarUploader';
import ModuleWidgets from 'corefacility-base/shared-view/components/ModuleWidgets';

import CoreWindowHeader from '../../base/CoreWindowHeader';
import styles from './style.module.css';


/** The form allows users to change their profile data and system administrators
 * 	to manage single users in the user list.
 */
export default class UserDetailForm extends UpdateForm{

	RELOAD_STATUS_CODES = [401, 403, 404];

	showDeletedObject = false;

	constructor(props){
		super(props);
		this.changePassword = this.changePassword.bind(this);
		this.printPassword = this.printPassword.bind(this);
		this.sendActivationCode = this.sendActivationCode.bind(this);
		this.setupAuthorizationMethod = this.setupAuthorizationMethod.bind(this);
		this.onAuthorizationWidgetsEmpty = this.onAuthorizationWidgetsEmpty.bind(this);

		this.state = {
			...this.state,
			showAuthorizationWidgets: true,
		}
	}

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return User;
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return [
			'login',
			'is_password_set',
			'name',
			'surname',
			'email',
			'phone',
			'unix_group',
			'home_dir',
			'is_locked',
			'is_superuser',
			'can_be_activated_using_email',
		];
	}

	/** Redirection route for "Save and close" and "Close" buttons
	 */
	get entityListRoute(){
		return "/users/";
	}

	/** Asks the user whether he wants to delete the form object
	 */
	async promptDelete(event){
		return await window.application.openModal("question", {
			caption: t("User delete confirmation"),
			prompt: t("This operation will permanently remove the user account, reset all user's membership in groups. ") +
				t("All user's personal files will also be permanently deleted from the cloud storage. ") + 
				t("Are you wish to continue?"),
		});
	}

	async changePassword(event, method){
		try{
			this.setState({inactive: true});
			this.setChildError("password", null);
			await method(event);
		} catch (error){
			if (this.RELOAD_STATUS_CODES.indexOf(error.status) !== -1){
				window.location.reload();
			}
			this.setChildError("password", error.message);
		} finally {
			this.setState({inactive: false});
		}
	}

	async doSuggestedAction(action){
		while (true){
			try{
				await action();
				return true;
			} catch (error){
				if (error instanceof BadRequestError && error.name === "action_required"){
					let result = await this.processPosixError(error);
					if (!result){
						return false;
					}
				} else {
					throw error;
				}
			}
		}
	}

	async printPassword(event){
		let apiVersion = window.SETTINGS.client_version;
		let path = `/api/${apiVersion}/users/${this._formObject.id}/password-reset/`;
		let response = await client.post(path, {});
		tpl_password(this._formObject.login, response.password);
	}

	async sendActivationCode(event){
		let apiVersion = window.SETTINGS.client_version;
		let path = `/api/${apiVersion}/users/${this._formObject.id}/activation-mail/`;
		await client.post(path, {});
		await window.application.openModal("message", {
			title: t("Account activation"),
			body: t("The activation mail has been successfully sent to the user."),
		});
	}

	/** Adjusts the authorization widget settings
	 * 	@param {ModuleWidget} authorizationWidget the widget to be adjusted
	 */
	async setupAuthorizationMethod(authorizationWidget){
		if (this.props.onAuthorizationMethodSetup){
			this.props.onAuthorizationMethodSetup(this._formObject, authorizationWidget);
		}
	}

	/** Triggers when no active authorization widgets have been loaded
	 */
	onAuthorizationWidgetsEmpty(){
		this.setState({
			showAuthorizationWidgets: false,
		});
	}

	/** Handles press on the "Remove" button that has to delete the _formObject
	 * 	from all external service
	 */
	async handleDelete(event){
		let result = await super.handleDelete(event);
		if (result === true && (window.SETTINGS.unix_administration || window.SETTINGS.suggest_administration)){
			await window.application.openModal('message', {
				title: t("Delete user"),
				body: t("The user will be deleted within the following several minutes."),
			});
		}
		return result;
	}

	/**	Transforms Javascript exception to the error message in the message bar.
	 * 
	 * 	@param {Error} error Javascript exception
	 * 	@param {function} tryAgainFunction an optional parameter. If tryAgainFunction is not null or undefined,
	 * 		the user receives "Action required" dialog box and presses Continue, the tryAgainFunction will be executed.
	 * 	@return {string} globalError the global error to lift up the state, true on success, false on fail.
	 */
	async handleError(error, tryAgainFunction){
		if (error instanceof BadRequestError && error.name === 'GroupGovernorConstraintFails'){
			let allowToForce = await window.application.openModal('question', {
				caption: t("User delete confirmation"),
				prompt: error.message,
			});
			if (allowToForce){
				return await tryAgainFunction(true);
			} else {
				return false;
			}
		} else if (error instanceof BadRequestError && error.name === 'ProjectRootGroupConstraintFails' &&
			(window.SETTINGS.unix_administration || window.SETTINGS.suggest_administration)) {
			this.setState({
				inactive: false,
				errors: {},
				globalError: t("The cascade user remove mechanism doesn't work in full server or part server " +
					"configuration. Please, remove all extra groups or extra projects manually.")
			});
			return false;
		} else {
			return await super.handleError(error, tryAgainFunction);
		}
	}

	renderContent(){
		let unset = <i className={styles.unset}>{t('Not defined.')}</i>;
		let header;
		if (this._formValues && (this._formValues.surname || this._formValues.name)){
			header = `${this._formValues.surname || ''} ${this._formValues.name || ''}`;
		} else {
			header = t("User information");
		}

		if (this.props.setBrowserTitle){
			this.props.setBrowserTitle(header);
		}

		let passwordSetMessage = null;
		if (this.state.rawValues.is_password_set){
			passwordSetMessage = t("The password was set.");
		} else {
			passwordSetMessage = t("The password was not set.");
		}

		let can_be_activated_using_email = false;
		if (this._formValues){
			can_be_activated_using_email = this._formValues.can_be_activated_using_email;
		}

		return (
			<CoreWindowHeader
				{...this.getMessageBarProps()}
				header={header}
				>
					<Scrollable>
						<form className={`${styles.main} window-form`}>
							<div className={styles.personal_data_row}>
								<section className={styles.personal_data}>
									<h2>{t("Personal Data")}</h2>
									<div className={styles.widgets}>
										<Label>{t('Login') + " *"}</Label>
										<TextInput
											{...this.getFieldProps('login')}
											htmlType="text"
											tooltip={t("The login is required for the user identification process during authentication")}
											maxLength={100}
										/>
										<Label>{t('First name')}</Label>
										<TextInput
											{...this.getFieldProps('name')}
											htmlType="text"
											tooltip={t("The first name is required for better visualization")}
											maxLength={100}
										/>
										<Label>{t('Last name')}</Label>
										<TextInput
											{...this.getFieldProps('surname')}
											htmlType="text"
											tooltip={t("The last name is required for better visualization")}
											maxLength={100}
										/>
										<Label>{t('E-mail')}</Label>
										<TextInput
											{...this.getFieldProps('email')}
											htmlType="email"
											tooltip={t("The e-mail will be used for password recovery service and sending another notifications")}
											maxLength={254}
										/>
										<Label>{t('Phone number')}</Label>
										<TextInput
											{...this.getFieldProps('phone')}
											htmlType="phone"
											tooltip={t("When suspicious activity was detected, please, call the user using this phone number: the user can confirm or deny this operation")}
											maxLength={20}
										/>
										<Label>{t('UNIX account name')}</Label>
										<Label>{this.state.rawValues.unix_group || unset}</Label>
										<Label>{t('Home directory')}</Label>
										<Label>{this.state.rawValues.home_dir || unset}</Label>
									</div>
								</section>
								<section className={styles.avatar_box}>
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
							<div className={styles.administration_row}>
								<section className={styles.password_changer}>
									<h2>{t("User's password")}</h2>
									<p className={styles.changer_message}>{passwordSetMessage}</p>
									<div className={styles.changer_button}>
										<Hyperlink onClick={event => this.changePassword(event, this.printPassword)} inactive={this.state.inactive}>
											{t("Print password")}
										</Hyperlink>
									</div>
									{window.SETTINGS.email_support && can_be_activated_using_email && <div className={styles.changer_button}>
											<Hyperlink
												onClick={event => this.changePassword(event, this.sendActivationCode)}
												inactive={this.state.inactive}
											>
												{t("Send activation code")}
											</Hyperlink>
										</div>
									}
									{ this.state.noFieldErrors.password && <p className={styles.changer_error}>{this.state.noFieldErrors.password}</p> }
								</section>
								<section className={styles.administration}>
									<h2>{t("Administration")}</h2>
									<CheckboxInput
										{...this.getFieldProps('is_locked')}
										label={t("Locked")}
										tooltip={t("The user can't authorize when he's locked.")}
									/>
									<CheckboxInput
										{...this.getFieldProps('is_superuser')}
										label={t("Superuser")}
										tooltip={t("Superuser has full access data and features in corefacility as well as in every its application")}
									/>
								</section>
							</div>
							{this.state.showAuthorizationWidgets && <div className={styles.widgets_row}>
								<section>
									<h2>{t("Authorization methods")}</h2>
									<ModuleWidgets
										parentModuleUuid={window.application.model.uuid}
										entryPointAlias="authorizations"
										onClick={this.setupAuthorizationMethod}
										inactive={this.state.inactive}
										onWidgetsEmpty={this.onAuthorizationWidgetsEmpty}
									/>
								</section>
							</div>}
							{this.renderEntityState()}
							<div className={styles.controls_row}>
								<PrimaryButton {...this.getSubmitProps()}>{t('Save')}</PrimaryButton>
								<PrimaryButton {...this.getSubmitProps()} onClick={this.handleSubmitAndClose}>{t('Save and close')}</PrimaryButton>
								<PrimaryButton
									type="cancel"
									inactive={this.state.inactive}
									onClick={this.handleClose}
									>
										{t('Close without save')}
								</PrimaryButton>
								<PrimaryButton
									type="remove"
									inactive={this.state.inactive}
									onClick={this.handleDelete}
									>
										{t('Remove')}
								</PrimaryButton>
							</div>
						</form>
					</Scrollable>
			</CoreWindowHeader>
		);
	}

	async componentDidUpdate(prevProps, prevState){
		if ((prevState.rawValues.name !== this.state.rawValues.name ||
			prevState.rawValues.surname !== this.state.rawValues.surname) &&
			this.props.onNameChange){
			if (!this._formValues.surname || !this._formValues.name){
				this.props.onNameChange(null);
			} else {
				this.props.onNameChange(`${this._formValues.surname} ${this._formValues.name}`);
			}
		}
	}

}